from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.ticket_service import TicketService
from services.user_service import UserService
from infrastructure.repositories.ticket_repository import TicketRepository
from infrastructure.repositories.user_repository import UserRepository
from api.schemas.ticket import TicketRequestSchema, TicketResponseSchema
from datetime import datetime
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
                  description: Status of the ticket (optional, defaults to Available)
              required:
                - EventName
                - EventDate
                - Price
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
        current_user_id = int(get_jwt_identity())
        
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
            EventName=data['EventName'],
            EventDate=data['EventDate'],
            Price=data['Price'],
            Status=data['Status'],
            OwnerID=data['OwnerID']
        )
        return jsonify(response_schema.dump(ticket)), 201
    except Exception as e:
        return jsonify({"message": "Error creating ticket", "error": str(e)}), 500

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
              required:
                - EventName
                - EventDate
                - Price
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
        current_user_id = int(get_jwt_identity())
        
        # Check if ticket exists and belongs to current user
        existing_ticket = ticket_service.get_ticket(ticket_id)
        if not existing_ticket:
            return jsonify({'message': 'Ticket not found'}), 404
        
        if existing_ticket.OwnerID != current_user_id:
            return jsonify({"message": "Forbidden - Can only update your own tickets"}), 403
        
        # Add OwnerID to data (keep the same owner)
        data['OwnerID'] = current_user_id
            
        errors = request_schema.validate(data)
        if errors:
            return jsonify({"message": "Validation errors", "errors": errors}), 400
        
        ticket = ticket_service.update_ticket(
            ticket_id=ticket_id,
            EventName=data['EventName'],
            EventDate=data['EventDate'],
            Price=data['Price'],
            Status=data.get('Status', 'Available'),
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
        current_user_id = int(get_jwt_identity())
        
        # Get all tickets and filter by current user
        all_tickets = ticket_service.list_tickets()
        my_tickets = [ticket for ticket in all_tickets if ticket.OwnerID == current_user_id]
        
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
        
        # Get all tickets and filter by owner
        all_tickets = ticket_service.list_tickets()
        owner_tickets = [ticket for ticket in all_tickets if ticket.OwnerID == owner_id]
        
        return jsonify(response_schema.dump(owner_tickets, many=True)), 200
    except Exception as e:
        return jsonify({"message": "Error retrieving tickets", "error": str(e)}), 500

@bp.route('/search', methods=['GET'])
def search_tickets():
    """
    Search tickets with filters
    ---
    get:
      summary: Search tickets with filters
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
        - name: date_from
          in: query
          schema:
            type: string
            format: date-time
          description: Start date
        - name: date_to
          in: query
          schema:
            type: string
            format: date-time
          description: End date
        - name: ticket_type
          in: query
          schema:
            type: string
            enum: [VIP, Premium, Standard, Economy]
          description: Ticket type filter
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
        for key in ['event_name', 'event_type', 'min_price', 'max_price', 'location', 
                   'date_from', 'date_to', 'ticket_type']:
            value = request.args.get(key)
            if value:
                if key in ['min_price', 'max_price']:
                    filters[key] = float(value)
                elif key in ['date_from', 'date_to']:
                    filters[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    filters[key] = value
        
        tickets = ticket_service.search_tickets(**filters)
        return jsonify(response_schema.dump(tickets, many=True)), 200
    except Exception as e:
        return jsonify({"message": "Error searching tickets", "error": str(e)}), 500

@bp.route('/trending', methods=['GET'])
def get_trending_tickets():
    """
    Get trending tickets
    ---
    get:
      summary: Get trending tickets
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

@bp.route('/<int:ticket_id>/reserve', methods=['POST'])
@jwt_required()
def reserve_ticket(ticket_id):
    """
    Reserve a ticket
    ---
    post:
      summary: Reserve a ticket
      security:
        - BearerAuth: []
      parameters:
        - name: ticket_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the ticket to reserve
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                reservation_duration:
                  type: integer
                  minimum: 1
                  maximum: 24
                  description: Reservation duration in hours
                buyer_message:
                  type: string
                  maxLength: 500
                  description: Message to seller
      tags:
        - Tickets
      responses:
        200:
          description: Ticket reserved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TicketResponse'
        400:
          description: Invalid request
        404:
          description: Ticket not found
        409:
          description: Ticket already reserved
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "No data provided"}), 400
        
        reservation_duration = data.get('reservation_duration', 2)
        buyer_message = data.get('buyer_message', '')
        
        ticket = ticket_service.reserve_ticket(ticket_id, current_user_id, 
                                             reservation_duration, buyer_message)
        return jsonify(response_schema.dump(ticket)), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error reserving ticket", "error": str(e)}), 500

@bp.route('/<int:ticket_id>/buy', methods=['POST'])
@jwt_required()
def buy_ticket(ticket_id):
    """
    Buy a ticket
    ---
    post:
      summary: Buy a ticket
      security:
        - BearerAuth: []
      parameters:
        - name: ticket_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the ticket to buy
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                payment_method:
                  type: string
                  enum: [Cash, Bank Transfer, Digital Wallet, Credit Card]
                  description: Payment method
                buyer_message:
                  type: string
                  maxLength: 500
                  description: Message to seller
      tags:
        - Tickets
      responses:
        200:
          description: Ticket purchased successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TicketResponse'
        400:
          description: Invalid request
        404:
          description: Ticket not found
        409:
          description: Ticket not available
    """
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "No data provided"}), 400
        
        payment_method = data.get('payment_method', 'Digital Wallet')
        buyer_message = data.get('buyer_message', '')
        
        ticket = ticket_service.buy_ticket(ticket_id, current_user_id, 
                                         payment_method, buyer_message)
        return jsonify(response_schema.dump(ticket)), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": "Error buying ticket", "error": str(e)}), 500

@bp.route('/<int:ticket_id>', methods=['DELETE'])
@jwt_required()
def delete_ticket(ticket_id):
    """
    Delete a ticket by ID (owner only)
    ---
    delete:
      summary: Delete a ticket by ID
      security:
        - BearerAuth: []
      parameters:
        - name: ticket_id
          in: path
          required: true
          schema:
            type: integer
          description: ID of the ticket to delete
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
        current_user_id = int(get_jwt_identity())
        
        # Check if ticket exists and belongs to current user
        existing_ticket = ticket_service.get_ticket(ticket_id)
        if not existing_ticket:
            return jsonify({'message': 'Ticket not found'}), 404
        
        if existing_ticket.OwnerID != current_user_id:
            return jsonify({"message": "Forbidden - Can only delete your own tickets"}), 403
        
        success = ticket_service.delete_ticket(ticket_id)
        return '', 204
    except Exception as e:
        return jsonify({"message": "Error deleting ticket", "error": str(e)}), 500
