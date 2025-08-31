from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.jwt_helpers import get_current_user_id
from services.ticket_service import TicketService
from services.user_service import UserService
from infrastructure.repositories.ticket_repository import TicketRepository
from infrastructure.repositories.user_repository import UserRepository
from api.schemas.ticket import TicketRequestSchema, TicketResponseSchema
from infrastructure.databases.mssql import session

bp = Blueprint('ticket', __name__, url_prefix='/tickets')

ticket_service = TicketService(TicketRepository(session))
user_service = UserService(UserRepository(session))
request_schema = TicketRequestSchema()
response_schema = TicketResponseSchema()

@bp.route('/', methods=['GET'])
def list_tickets():
    """
    Get all tickets
    ---
    get:
      summary: Get all tickets
      tags:
        - Tickets
      responses:
        200:
          description: List of tickets
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TicketResponse'
        500:
          description: Internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    try:
        tickets = ticket_service.list_tickets()
        return jsonify(response_schema.dump(tickets, many=True)), 200
    except Exception as e:
        return jsonify({"message": "Error retrieving tickets", "error": str(e)}), 500

@bp.route('/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """
    Get ticket by ID
    ---
    get:
      summary: Get ticket by ID
      parameters:
        - name: ticket_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the ticket to retrieve
      tags:
        - Tickets
      responses:
        200:
          description: Ticket details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TicketResponse'
        404:
          description: Ticket not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        500:
          description: Internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    try:
        ticket = ticket_service.get_ticket(ticket_id)
        if not ticket:
            return jsonify({'message': 'Ticket not found'}), 404
        return jsonify(response_schema.dump(ticket)), 200
    except Exception as e:
        return jsonify({"message": "Error retrieving ticket", "error": str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_ticket():
    """
    Create a new ticket
    ---
    post:
      summary: Create a new ticket
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                EventName:
                  type: string
                  description: Name of the event
                EventDate:
                  type: string
                  format: date-time
                  description: Date and time of the event
                Price:
                  type: number
                  description: Price of the ticket
                Status:
                  type: string
                  enum: [Available, Sold, Reserved, Cancelled]
                  description: Status of the ticket
                ContactInfo:
                  type: string
                  description: Contact information for the seller
                PaymentMethod:
                  type: string
                  enum: [Cash, Bank Transfer, Digital Wallet, Credit Card]
                  description: Preferred payment method
              required:
                - EventName
                - EventDate
                - Price
                - Status
                - ContactInfo
                - PaymentMethod
      tags:
        - Tickets
      responses:
        201:
          description: Ticket created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TicketResponse'
        400:
          description: Invalid input data
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                  errors:
                    type: object
        401:
          description: Unauthorized - Invalid or missing JWT token
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        500:
          description: Internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        # Get current user ID from JWT token
        current_user_id = get_current_user_id()
        
        # Add OwnerID to data
        data['OwnerID'] = current_user_id
            
        errors = request_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400

        # Validate current user exists
        owner = user_service.get_user(current_user_id)
        if not owner:
            return jsonify({"message": "User not found"}), 404
        
        # Set default status if not provided
        if 'Status' not in data or not data['Status']:
            data['Status'] = 'Available'
        
        ticket = ticket_service.create_ticket(
            EventDate=data['EventDate'],
            Price=data['Price'],
            EventName=data['EventName'],
            Status=data['Status'],
            PaymentMethod=data['PaymentMethod'],
            ContactInfo=data['ContactInfo'],
            OwnerID=data['OwnerID']
        )
        return jsonify(response_schema.dump(ticket)), 201
    except Exception as e:
        return jsonify({"message": "Error creating ticket", "error": str(e)}), 500

@bp.route('/<int:ticket_id>', methods=['GET'])
def get_ticket_by_id(ticket_id):
    """
    Get ticket by ID
    ---
    get:
      summary: Get ticket by ID
      parameters:
        - name: ticket_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the ticket to get
      tags:
        - Tickets
      responses:
        200:
          description: Ticket details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TicketResponse'
        404:
          description: Ticket not found
    """
    try:
        ticket = ticket_service.get_ticket(ticket_id)
        if not ticket:
            return jsonify({"message": "Ticket not found"}), 404

        return jsonify(response_schema.dump(ticket)), 200
    except Exception as e:
        return jsonify({"message": "Error retrieving ticket", "error": str(e)}), 500

@bp.route('/<int:ticket_id>', methods=['PUT'])
@jwt_required()
def update_ticket(ticket_id):
    """
    Update a ticket by ID (owner only)
    ---
    put:
      summary: Update a ticket by ID
      security:
        - BearerAuth: []
      parameters:
        - name: ticket_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the ticket to update
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                EventName:
                  type: string
                  description: Name of the event
                EventDate:
                  type: string
                  format: date-time
                  description: Date and time of the event
                Price:
                  type: number
                  description: Price of the ticket
                Status:
                  type: string
                  enum: [Available, Sold, Reserved, Cancelled]
                  description: Status of the ticket
                ContactInfo:
                  type: string
                  description: Contact information for the seller
                PaymentMethod:
                  type: string
                  enum: [Cash, Bank Transfer, Digital Wallet, Credit Card]
                  description: Preferred payment method
              required:
                - EventName
                - EventDate
                - Price
                - ContactInfo
                - PaymentMethod
                - Status
      tags:
        - Tickets
      responses:
        200:
          description: Ticket updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TicketResponse'
        400:
          description: Invalid input data
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                  errors:
                    type: object
        403:
          description: Forbidden - Can only update your own tickets
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        404:
          description: Ticket not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        500:
          description: Internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400
            
        # Get current user ID from JWT token
        current_user_id = get_current_user_id()

        # Check if ticket exists and belongs to current user
        existing_ticket = ticket_service.get_ticket(ticket_id)
        if not existing_ticket:
            return jsonify({'message': 'Ticket not found'}), 404

        if existing_ticket.OwnerID != current_user_id:
            return jsonify({"message": "Forbidden - Can only update your own tickets"}), 403
        data['OwnerID'] = current_user_id
            
        errors = request_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        # Only update status if provided in request
        status = data.get('Status', existing_ticket.Status)
        
        ticket = ticket_service.update_ticket(
            ticket_id=existing_ticket.TicketID,
            EventName=data['EventName'],
            EventDate=data['EventDate'],
            Price=data['Price'],
            Status=status,
            PaymentMethod=data['PaymentMethod'],
            ContactInfo=data['ContactInfo'],
            OwnerID=data['OwnerID']
        )
        return jsonify(response_schema.dump(ticket)), 200
    except Exception as e:
        return jsonify({"message": "Error updating ticket", "error": str(e)}), 500

@bp.route('/my-tickets', methods=['GET'])
@jwt_required()
def get_my_tickets():
    """
    Get current user's tickets
    ---
    get:
      summary: Get current user's tickets
      security:
        - BearerAuth: []
      tags:
        - Tickets
      responses:
        200:
          description: List of current user's tickets
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TicketResponse'
        401:
          description: Unauthorized - Invalid or missing JWT token
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        500:
          description: Internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    try:
        # Get current user ID from JWT token
        current_user_id = get_current_user_id()
        
        # Get tickets by owner using efficient method
        my_tickets = ticket_service.get_tickets_by_owner(current_user_id)
        
        return jsonify(response_schema.dump(my_tickets, many=True)), 200
    except Exception as e:
        return jsonify({"message": "Error retrieving tickets", "error": str(e)}), 500

@bp.route('/owner/<int:owner_id>', methods=['GET'])
def get_tickets_by_owner(owner_id):
    """
    Get tickets by owner ID
    ---
    get:
      summary: Get tickets by owner ID
      parameters:
        - name: owner_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the owner to get tickets for
      tags:
        - Tickets
      responses:
        200:
          description: List of tickets for the owner
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TicketResponse'
        404:
          description: Owner not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        500:
          description: Internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    try:
        # Validate owner exists
        owner = user_service.get_user(owner_id)
        if not owner:
            return jsonify({"message": "Owner not found"}), 404
        
        # Get tickets by owner using efficient method
        owner_tickets = ticket_service.get_tickets_by_owner(owner_id)
        
        return jsonify(response_schema.dump(owner_tickets, many=True)), 200
    except Exception as e:
        return jsonify({"message": "Error retrieving tickets", "error": str(e)}), 500

@bp.route('/search', methods=['GET'])
def search_tickets():
    """
    Search tickets by event name
    ---
    get:
      summary: Search tickets by event name
      parameters:
        - name: event_name
          in: query
          required: true
          schema:
            type: string
          description: Event name to search, required
      tags:
        - Tickets
      responses:
        200:
          description: List of matching tickets
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TicketResponse'
        400:
          description: Missing event_name parameter
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        500:
          description: Internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    try:
        event_name = request.args.get('event_name')
        if not event_name:
            return jsonify({"message": "event_name parameter is required"}), 400
        
        tickets = ticket_service.search_tickets_by_event_name(event_name)
        return jsonify(response_schema.dump(tickets, many=True)), 200
    except Exception as e:
        return jsonify({"message": "Error searching tickets", "error": str(e)}), 500

@bp.route('/search/advanced', methods=['GET'])
def search_tickets_advanced():
    """
    Advanced search tickets with multiple filters
    ---
    get:
      summary: Advanced search tickets with multiple filters
      parameters:
        - name: event_name
          in: query
          schema:
            type: string
          description: Event name to search
        - name: event_type
          in: query
          schema:
            type: string
            enum: [Concert, Sports, Theater, Conference, Other]
          description: Event type filter
        - name: min_price
          in: query
          schema:
            type: number
          description: Minimum price
        - name: max_price
          in: query
          schema:
            type: number
          description: Maximum price
        - name: location
          in: query
          schema:
            type: string
          description: Event location
        - name: ticket_type
          in: query
          schema:
            type: string
            enum: [VIP, Premium, Standard, Economy]
          description: Ticket type filter
        - name: is_negotiable
          in: query
          schema:
            type: boolean
          description: Negotiable filter
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
          description: Number of results to return
      tags:
        - Tickets
      responses:
        200:
          description: List of matching tickets
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TicketResponse'
    """
    try:
        filters = {}
        for key in ['event_name', 'event_type', 'min_price', 'max_price', 
                   'location', 'ticket_type', 'is_negotiable', 'limit']:
            value = request.args.get(key)
            if value:
                if key in ['min_price', 'max_price']:
                    filters[key] = float(value)
                elif key == 'is_negotiable':
                    filters[key] = value.lower() == 'true'
                elif key == 'limit':
                    filters[key] = int(value)
                else:
                    filters[key] = value
        
        tickets = ticket_service.search_tickets_advanced(**filters)
        return jsonify(response_schema.dump(tickets, many=True)), 200
    except Exception as e:
        return jsonify({"message": "Error searching tickets", "error": str(e)}), 500

@bp.route('/trending', methods=['GET'])
def get_trending_tickets():
    """
    Get trending tickets
    ---
    get:
      summary: Get trending tickets based on view count and rating
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 10
          description: Number of tickets to return
      tags:
        - Tickets
      responses:
        200:
          description: List of trending tickets
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TicketResponse'
    """
    try:
        limit = int(request.args.get('limit', 10))
        tickets = ticket_service.get_trending_tickets(limit)
        return jsonify(response_schema.dump(tickets, many=True)), 200
    except Exception as e:
        return jsonify({"message": "Error getting trending tickets", "error": str(e)}), 500

@bp.route('/event-type/<event_type>', methods=['GET'])
def get_tickets_by_event_type(event_type):
    """
    Get tickets by event type
    ---
    get:
      summary: Get tickets by event type
      parameters:
        - name: event_type
          in: path
          required: true
          schema:
            type: string
            enum: [Concert, Sports, Theater, Conference, Other]
          description: Event type to filter by
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
          description: Number of tickets to return
      tags:
        - Tickets
      responses:
        200:
          description: List of tickets by event type
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/TicketResponse'
    """
    try:
        limit = int(request.args.get('limit', 20))
        tickets = ticket_service.get_tickets_by_event_type(event_type, limit)
        return jsonify(response_schema.dump(tickets, many=True)), 200
    except Exception as e:
        return jsonify({"message": "Error getting tickets by event type", "error": str(e)}), 500

@bp.route('/<int:ticket_id>/view', methods=['POST'])
def increment_view_count(ticket_id):
    """
    Increment view count for a ticket
    ---
    post:
      summary: Increment view count for a ticket
      parameters:
        - name: ticket_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the ticket
      tags:
        - Tickets
      responses:
        200:
          description: View count incremented successfully
        404:
          description: Ticket not found
    """
    try:
        ticket = ticket_service.get_ticket(ticket_id)
        if not ticket:
            return jsonify({'message': 'Ticket not found'}), 404
        
        ticket_service.increment_view_count(ticket_id)
        return jsonify({"message": "View count incremented"}), 200
    except Exception as e:
        return jsonify({"message": "Error incrementing view count", "error": str(e)}), 500

@bp.route('/<int:ticket_id>/rate', methods=['POST'])
@jwt_required()
def rate_ticket(ticket_id):
    """
    Rate a ticket
    ---
    post:
      summary: Rate a ticket (1-5 stars)
      security:
        - BearerAuth: []
      parameters:
        - name: ticket_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the ticket to rate
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                rating:
                  type: number
                  minimum: 0
                  maximum: 5
                  description: Rating value, range 0-5
              required:
                - rating
      tags:
        - Tickets
      responses:
        200:
          description: Rating updated successfully
        400:
          description: Invalid rating value
        404:
          description: Ticket not found
    """
    try:
        data = request.get_json()
        if not data or 'rating' not in data:
            return jsonify({"message": "Rating is required"}), 400
        
        rating = float(data['rating'])
        if not (0 <= rating <= 5):
            return jsonify({"message": "Rating must be between 0 and 5"}), 400
        
        ticket = ticket_service.get_ticket(ticket_id)
        if not ticket:
            return jsonify({'message': 'Ticket not found'}), 404
        
        ticket_service.update_rating(ticket_id, rating)
        return jsonify({"message": "Rating updated successfully"}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": "Error updating rating", "error": str(e)}), 500

@bp.route('/<event_name>/<owner_username>', methods=['DELETE'])
@jwt_required()
def delete_ticket(event_name, owner_username):
    """
    Delete a ticket by event name and owner username (owner only)
    ---
    delete:
      summary: Delete a ticket by event name and owner username
      security:
        - BearerAuth: []
      parameters:
        - name: event_name
          in: path
          required: true
          schema:
            type: string
          description: Name of the event
        - name: owner_username
          in: path
          required: true
          schema:
            type: string
          description: Username of the ticket owner
      tags:
        - Tickets
      responses:
        204:
          description: Ticket deleted successfully
        403:
          description: Forbidden - Can only delete your own tickets
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        404:
          description: Ticket not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
        500:
          description: Internal server error
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    try:
        # Get current user ID from JWT token
        current_user_id = get_current_user_id()

        # Check if ticket exists and belongs to current user
        existing_ticket = ticket_service.get_ticket_by_event_and_owner(event_name, owner_username)
        if not existing_ticket:
            return jsonify({'message': 'Ticket not found'}), 404

        if existing_ticket.OwnerID != current_user_id:
            return jsonify({"message": "Forbidden - Can only delete your own tickets"}), 403

        success = ticket_service.delete_ticket(existing_ticket.TicketID)
        return '', 204
    except Exception as e:
        return jsonify({"message": "Error deleting ticket", "error": str(e)}), 500
