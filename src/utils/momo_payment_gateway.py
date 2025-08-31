import hmac
import json
import uuid
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import hashlib

logger = logging.getLogger(__name__)

class MomoPaymentGateway:
    def __init__(self, partner_code: str, access_key: str, secret_key: str, api_endpoint: str):
        """
        Initialize MoMo Payment Gateway
        
        Args:
            partner_code: MoMo Partner Code
            access_key: MoMo Access Key
            secret_key: MoMo Secret Key
            api_endpoint: MoMo API Endpoint (sandbox or production)
        """
        self.partner_code = partner_code
        self.access_key = access_key
        self.secret_key = secret_key
        self.api_endpoint = api_endpoint
    
    def create_payment_request(self, 
                               order_id: str, 
                               amount: int, 
                               order_info: str, 
                               return_url: str, 
                               notify_url: str,
                               extra_data: str = "",
                               bank_code: Optional[str] = None,
                               card_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a payment request to MoMo
        
        Args:
            order_id: Unique order ID
            amount: Payment amount (in VND)
            order_info: Order description
            return_url: URL to redirect user after payment
            notify_url: URL for MoMo to send payment notification
            extra_data: Additional data to include in the request
            
        Returns:
            Dict with payment request result including payUrl
        """
        # Create request data
        request_id = str(uuid.uuid4())
        request_type = "payWithATM"
        
        # Convert amount to integer as required by MoMo
        amount = int(amount)
        
        # Create raw signature
        # Create raw signature by sorting parameters alphabetically
        # Xây chuỗi chữ ký đúng thứ tự theo tài liệu MoMo
        raw_signature = (
            f"accessKey={self.access_key}&"
            f"amount={amount}&"
            f"extraData={extra_data}&"
            f"ipnUrl={notify_url}&"
            f"orderId={order_id}&"
            f"orderInfo={order_info}&"
            f"partnerCode={self.partner_code}&"
            f"redirectUrl={return_url}&"
            f"requestId={request_id}&"
            f"requestType={request_type}"
        )
        if bank_code:
            raw_signature += f"&bankCode={bank_code}"
        if card_token:
            raw_signature += f"&cardToken={card_token}"
        
        # Create signature
        h = hmac.new(bytes(self.secret_key, 'utf-8'), bytes(raw_signature, 'utf-8'), hashlib.sha256)
        logger.debug(f"Raw signature for MoMo: {raw_signature}")
        signature = h.hexdigest()
        
        # Create request body
        data = {
            "partnerCode": self.partner_code,
            "accessKey": self.access_key,
            "requestId": request_id,
            "amount": amount,
            "orderId": order_id,
            "orderInfo": order_info,
            "redirectUrl": return_url,
            "ipnUrl": notify_url,
            "extraData": extra_data,
            "requestType": request_type,
            "signature": signature,
            "lang": "vi"
        }
        if bank_code:
            data["bankCode"] = bank_code
        if card_token:
            data["cardToken"] = card_token
        
        logger.info(f"Creating MoMo payment request for order {order_id} with amount {amount}")
        
        try:
            # Send request to MoMo
            response = requests.post(self.api_endpoint, json=data)
            response_json = response.json()
            
            logger.info(f"MoMo payment request response for order {order_id}: {response_json}. Response time: {response_json.get('responseTime')}")
            
            return response_json
        except Exception as e:
            logger.error(f"Error creating MoMo payment request: {e}")
            raise ValueError(f"Failed to create MoMo payment: {e}")
    
    def verify_ipn_signature(self, ipn_params: Dict[str, Any]) -> bool:
        """
        Verify the signature of the IPN (Instant Payment Notification) from MoMo
        
        Args:
            ipn_params: Parameters received from MoMo IPN
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Extract parameters
        if 'signature' not in ipn_params:
            logger.error("Missing signature in IPN params")
            return False
            
        received_signature = ipn_params['signature']
        
        # List of fields to include in signature verification
        signature_fields = [
            'partnerCode', 'orderId', 'requestId', 'amount', 'orderInfo',
            'orderType', 'transId', 'resultCode', 'message', 'payType',
            'responseTime', 'extraData', 'accessKey'
        ]
        
        # Create raw signature string
        field_values = []
        for field in signature_fields:
            if field in ipn_params:
                field_values.append(f"{field}={ipn_params[field]}")
        
        raw_signature = "&".join(field_values)
        
        # Create signature
        h = hmac.new(bytes(self.secret_key, 'utf-8'), bytes(raw_signature, 'utf-8'), hashlib.sha256)
        calculated_signature = h.hexdigest()
        
        # Compare signatures
        is_valid = calculated_signature == received_signature
        
        if not is_valid:
            logger.warning(f"Invalid MoMo IPN signature. Calculated: {calculated_signature}, Received: {received_signature}")
        
        return is_valid
    
    def get_transaction_status(self, order_id: str, request_id: str) -> Dict[str, Any]:
        """
        Check the status of a transaction
        
        Args:
            order_id: Order ID
            request_id: Request ID
            
        Returns:
            Dict with transaction status
        """
        # Create raw signature
        raw_signature = f"accessKey={self.access_key}&orderId={order_id}&partnerCode={self.partner_code}&requestId={request_id}"
        
        # Create signature
        h = hmac.new(bytes(self.secret_key, 'utf-8'), bytes(raw_signature, 'utf-8'), hashlib.sha256)
        signature = h.hexdigest()
        
        # Create request body
        data = {
            "partnerCode": self.partner_code,
            "accessKey": self.access_key,
            "requestId": request_id,
            "orderId": order_id,
            "signature": signature
        }
        
        try:
            # Send request to MoMo
            query_url = self.api_endpoint.replace('/create', '/query')
            response = requests.post(query_url, json=data)
            response_json = response.json()
            
            logger.info(f"MoMo transaction status for order {order_id}: {response_json}")
            
            return response_json
        except Exception as e:
            logger.error(f"Error checking MoMo transaction status: {e}")
            raise ValueError(f"Failed to check MoMo transaction status: {e}")
    
    def process_payment_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment callback from MoMo and update payment status
        
        Args:
            callback_data: JSON data received from MoMo callback
            
        Returns:
            Dict with processing result
        """
        logger.info(f"Processing MoMo payment callback: {callback_data}")
        
        try:
            # Validate callback data structure
            required_fields = ['error_code', 'message', 'payment_id', 'status', 'transaction_id']
            for field in required_fields:
                if field not in callback_data:
                    error_msg = f"Missing required field in callback data: {field}"
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'message': error_msg
                    }
            
            # Extract important information
            error_code = callback_data.get('error_code')
            message = callback_data.get('message')
            payment_id = callback_data.get('payment_id')
            status = callback_data.get('status')
            transaction_id = callback_data.get('transaction_id')
            
            # Validate payment status
            if error_code != 0:
                logger.error(f"Payment failed with error code {error_code}: {message}")
                return {
                    'success': False,
                    'message': message,
                    'payment_id': payment_id,
                    'transaction_id': transaction_id
                }
            
            # Verify payment status
            if status != 'success':
                logger.warning(f"Unexpected payment status: {status}")
                return {
                    'success': False,
                    'message': f"Unexpected payment status: {status}",
                    'payment_id': payment_id,
                    'transaction_id': transaction_id
                }
            
            # Payment successful
            logger.info(f"Payment {payment_id} completed successfully with transaction ID {transaction_id}")
            return {
                'success': True,
                'message': message,
                'payment_id': payment_id,
                'transaction_id': transaction_id,
                'status': status
            }
            
        except Exception as e:
            error_msg = f"Error processing payment callback: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg
            }
