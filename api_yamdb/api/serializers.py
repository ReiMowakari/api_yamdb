from rest_framework.serializers import (
    ModelSerializer, IntegerField)

from reviews.models import Comment, Review

from .mixins import CommonFieldsCommentReviewMixin


class CommentSerializer(CommonFieldsCommentReviewMixin, ModelSerializer):

    class Meta(CommonFieldsCommentReviewMixin.Meta):
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class ReviewSerializer(CommonFieldsCommentReviewMixin, ModelSerializer):
    score = IntegerField(required=True)

    class Meta(CommonFieldsCommentReviewMixin.Meta):
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
