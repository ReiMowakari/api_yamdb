from rest_framework.serializers import (
    ModelSerializer, StringRelatedField, IntegerField)

from reviews.models import Comment, Review


class CommonFieldsCommentReviewMixin:
    """Общий миксин для полей для исключения кода."""

    author = StringRelatedField()

    class Meta:
        read_only_fields = ('id', 'author', 'pub_date')


class CommentSerializer(CommonFieldsCommentReviewMixin, ModelSerializer):

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment


class ReviewSerializer(CommonFieldsCommentReviewMixin, ModelSerializer):
    score = IntegerField(required=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
