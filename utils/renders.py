from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None
        
        if response is None:
            return super().render(data, accepted_media_type, renderer_context)
        
        status_code = response.status_code
        
        # Don't wrap if it's already wrapped (from your exception handler)
        # Your exception handler adds 'status' key, so we check for that
        if isinstance(data, dict) and 'status' in data:
            return super().render(data, accepted_media_type, renderer_context)
        
        # Wrap successful responses (2xx status codes)
        if 200 <= status_code < 300:
            wrapped_data = {
                'status': 'success',
                'message': self._get_success_message(renderer_context),
                'data': data
            }
        else:
            # This shouldn't normally happen as your exception_handler catches errors
            # But just in case, we handle it
            wrapped_data = {
                'status': 'error',
                'message': 'An error occurred',
                'data': {}
            }
        
        return super().render(wrapped_data, accepted_media_type, renderer_context)
    
    def _get_success_message(self, renderer_context):
        """Generate appropriate success message based on the request method"""
        if not renderer_context:
            return 'Operation successful'
        
        request = renderer_context.get('request')
        if not request:
            return 'Operation successful'
        
        method = request.method.upper()
        
        messages = {
            'GET': 'Data retrieved successfully',
            'POST': 'Resource created successfully',
            'PUT': 'Resource updated successfully',
            'PATCH': 'Resource updated successfully',
            'DELETE': 'Resource deleted successfully',
        }
        
        return messages.get(method, 'Operation successful')