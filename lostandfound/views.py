from rest_framework import viewsets, status
from rest_framework.decorators import action,  api_view
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404


class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = []
    serializer_class = ItemSerializer
    
    def get_queryset(self):
        """
        This method determines which items to return by filtering on query parameters
        """
        # Get the status parameter from the URL if it exists
        status = self.request.query_params.get('status', None)
        if status:
            return Item.objects.filter(status=status)
        # If no status specified, return all items
        return Item.objects.all()

    def perform_create(self, serializer):
        user_id = self.request.data.get("user")  # Get user ID from json body sent by request
        try:
            user = User.objects.get(id=user_id)
            serializer.save(user=user)
        except User.DoesNotExist:
            return Response({"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_claimed(self, request, pk=None): #self is viewset instance 
        
        item = self.get_object()
        if item.status == 'found':
            item.status = 'claimed'
            item.save()
            return Response({'status': 'item marked as claimed'})
        return Response(
            {'error': 'Can only claim found items'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post']) #deatil=True means action is performed on a single object
    def mark_resolved(self, request, pk=None):
        """
        Custom endpoint to mark an item as resolved
        Access it via POST /api/items/{id}/mark_resolved/
        """
        item = self.get_object()
        if item.status in ['lost', 'found']:
            item.status = 'resolved'
            item.save()
            return Response({'status': 'item marked as resolved'})
        return Response(
            {'error': 'Invalid status transition'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['get'])
    def match_items(self, request):
        matched_items = []

        # Get all lost items (excluding claimed and resolved)
        lost_items = Item.objects.filter(status="lost").exclude(status__in=['claimed', 'resolved'])

        for lost_item in lost_items:
            # Find one matching found item in the same category
            found_item = Item.objects.filter(
                status="found",
                category=lost_item.category
            ).exclude(status__in=['claimed', 'resolved']).first()  # Get only one match

            # If a match is found, add to the result list
            if found_item:
                matched_items.append({
                    "lost_item": self.get_serializer(lost_item).data,
                    "found_item": self.get_serializer(found_item).data
                })

        return Response(matched_items, status=status.HTTP_200_OK)
    
    @action(detail=False,methods=['delete'])
    def delete_item(self,request):
        # item_name=request.query_params.get('name')
        name=self.request.data.get('name')
        if not name:
            return Response({"error":"Item name required"},status=status.HTTP_400_BAD_REQUEST)
        item= get_object_or_404(Item, name=name)
        if item.status=="claimed":
            item.delete()
            return Response({"message": f"Item '{name}' has been deleted."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": f"Item '{name}' is not marked as claimed."}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def api_root(request, format=None):
   
    return Response({
        'all_items': {
            'url': reverse('item-list', request=request, format=format),
            'method': 'GET',
            'description': 'View all lost and found items'
        },
        'lost_items': {
            'url': reverse('item-list', request=request, format=format) + '?status=lost',
            'method': 'GET',
            'description': 'View only lost items'
        },
        'found_items': {
            'url': reverse('item-list', request=request, format=format) + '?status=found',
            'method': 'GET',
            'description': 'View only found items'
        },
        'create_item': {
            'url': reverse('item-list', request=request, format=format),
            'method': 'POST',
            'description': 'Create a new lost or found item',
            'fields': {
                'name': 'Name of the item',
                'description': 'Detailed description of the item',
                'location': 'Where the item was lost/found',
                'contact_info': 'How to contact the poster',
                'status': 'Either "lost" or "found"',
                'category': 'Item category (e.g., electronics, clothing)',
                'color': 'Main color of the item'
            }
        },
        'delete_item': {
            'url': reverse('item-delete-item', request=request, format=format),
            'method': 'DELETE',
            'description': 'Delete a claimed lost and found item'
        },
        'item_matching': {
            'url': reverse('item-match-items', request=request, format=format),
            'method': 'GET',
            'description': 'Find potential matches for an item',
            'parameters': {
                'item_id': 'ID of the item to find matches for'
            }
        },
        'mark_claimed': {
            'url': '/api/items/{id}/mark_claimed/',
            'method': 'POST',
            'description': 'Mark a found item as claimed by its owner'
        },
        'mark_resolved': {
            'url': '/api/items/{id}/mark_resolved/',
            'method': 'POST',
            'description': 'Mark an item as resolved'
        }
    })
