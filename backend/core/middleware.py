from django.http import HttpResponse

class VercelCORSMiddleware:
    """
    Middleware personnalisé pour gérer les requêtes CORS provenant de Vercel.
    Permet de contourner les limitations de la bibliothèque standard avec les URLs de prévisualisation.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Pour les requêtes OPTIONS (preflight)
        if request.method == "OPTIONS":
            origin = request.META.get('HTTP_ORIGIN')
            if origin and ('.vercel.app' in origin or 'localhost' in origin):
                response = HttpResponse(status=200)
                response["Access-Control-Allow-Origin"] = origin
                response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-CSRFToken, Access-Control-Allow-Origin"
                response["Access-Control-Allow-Credentials"] = "true"
                return response
        
        response = self.get_response(request)
        
        # Pour les autres requêtes, on s'assure que le header est présent si l'origine est Vercel
        origin = request.META.get('HTTP_ORIGIN')
        if origin and ('.vercel.app' in origin or 'localhost' in origin):
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            
        return response
