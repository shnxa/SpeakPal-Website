from rest_framework.viewsets import ModelViewSet
from applications.review.permissions import ReviewOwnerOrReadOnly
from applications.review.serializers import ReviewSerializer
from applications.review.models import Review


class ReviewModelViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [ReviewOwnerOrReadOnly]
    queryset = Review.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)