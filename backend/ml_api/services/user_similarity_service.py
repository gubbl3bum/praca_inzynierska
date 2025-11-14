import numpy as np
from collections import defaultdict
from django.db import transaction, models
from django.db.models import Q, Avg, Count
from sklearn.metrics.pairwise import cosine_similarity
from ..models import (
    User, UserSimilarity, UserPreferenceProfile, 
    BookReview, Category, Author, Publisher
)

class UserSimilarityService:
    """
    Service for calculating user similarities and generating collaborative recommendations
    """
    
    def __init__(self):
        self.min_similarity_threshold = 0.3
        self.weights = {
            'preference': 0.6,  # Profile preferences
            'rating': 0.4       # Rating patterns
        }
    
    def calculate_preference_similarity(self, user1_profile, user2_profile):
        """
        Calculate similarity based on preference profiles
        Uses category preferences, authors, publishers
        """
        if not user1_profile or not user2_profile:
            return 0.0
        
        similarities = []
        
        # Category similarity (weighted)
        cat1 = user1_profile.preferred_categories or {}
        cat2 = user2_profile.preferred_categories or {}
        
        if cat1 and cat2:
            all_cats = set(cat1.keys()) | set(cat2.keys())
            if all_cats:
                vec1 = np.array([cat1.get(cat, 0) for cat in all_cats])
                vec2 = np.array([cat2.get(cat, 0) for cat in all_cats])
                
                norm1 = np.linalg.norm(vec1)
                norm2 = np.linalg.norm(vec2)
                
                if norm1 > 0 and norm2 > 0:
                    cat_sim = np.dot(vec1, vec2) / (norm1 * norm2)
                    similarities.append(cat_sim * 0.6)  # 60% weight
        
        # Author similarity (Jaccard)
        auth1 = set(user1_profile.preferred_authors or [])
        auth2 = set(user2_profile.preferred_authors or [])
        
        if auth1 and auth2:
            intersection = len(auth1 & auth2)
            union = len(auth1 | auth2)
            if union > 0:
                auth_sim = intersection / union
                similarities.append(auth_sim * 0.3)  # 30% weight
        
        # Publisher similarity (Jaccard)
        pub1 = set(user1_profile.preferred_publishers or [])
        pub2 = set(user2_profile.preferred_publishers or [])
        
        if pub1 and pub2:
            intersection = len(pub1 & pub2)
            union = len(pub1 | pub2)
            if union > 0:
                pub_sim = intersection / union
                similarities.append(pub_sim * 0.1)  # 10% weight
        
        return sum(similarities) if similarities else 0.0
    
    def calculate_rating_similarity(self, user1, user2):
        """
        Calculate similarity based on rating patterns (collaborative filtering)
        Uses Pearson correlation on common books
        """
        # Get reviews from both users
        reviews1 = BookReview.objects.filter(user=user1).values('book_id', 'rating')
        reviews2 = BookReview.objects.filter(user=user2).values('book_id', 'rating')
        
        # Create rating dictionaries
        ratings1 = {r['book_id']: r['rating'] for r in reviews1}
        ratings2 = {r['book_id']: r['rating'] for r in reviews2}
        
        # Find common books
        common_books = set(ratings1.keys()) & set(ratings2.keys())
        
        if len(common_books) < 2:  # Need at least 2 common books
            return 0.0
        
        # Get ratings for common books
        vec1 = np.array([ratings1[book_id] for book_id in common_books])
        vec2 = np.array([ratings2[book_id] for book_id in common_books])
        
        # Calculate Pearson correlation
        mean1 = np.mean(vec1)
        mean2 = np.mean(vec2)
        
        diff1 = vec1 - mean1
        diff2 = vec2 - mean2
        
        numerator = np.sum(diff1 * diff2)
        denominator = np.sqrt(np.sum(diff1**2) * np.sum(diff2**2))
        
        if denominator == 0:
            return 0.0
        
        correlation = numerator / denominator
        
        # Normalize to 0-1 range
        return (correlation + 1) / 2
    
    def calculate_similarity_between_users(self, user1, user2):
        """
        Calculate combined similarity between two users
        """
        # Get preference profiles
        try:
            profile1 = user1.preference_profile
        except UserPreferenceProfile.DoesNotExist:
            profile1 = None
        
        try:
            profile2 = user2.preference_profile
        except UserPreferenceProfile.DoesNotExist:
            profile2 = None
        
        # Calculate component similarities
        pref_sim = self.calculate_preference_similarity(profile1, profile2)
        rating_sim = self.calculate_rating_similarity(user1, user2)
        
        # Combined similarity (weighted)
        combined = (
            pref_sim * self.weights['preference'] +
            rating_sim * self.weights['rating']
        )
        
        return {
            'preference_similarity': pref_sim,
            'rating_similarity': rating_sim,
            'combined_similarity': combined
        }
    
    def calculate_similarities_for_user(self, target_user, batch_size=50):
        """
        Calculate similarities for one user against all others
        """
        print(f"📊 Calculating user similarities for: {target_user.username}")
        
        # Get all other users (with reviews or profiles)
        other_users = User.objects.exclude(id=target_user.id).filter(
            models.Q(reviews__isnull=False) | 
            models.Q(preference_profile__isnull=False)
        ).distinct()
        
        total_users = other_users.count()
        similarities_created = 0
        
        print(f"👥 Processing {total_users} other users...")
        
        with transaction.atomic():
            # Delete old similarities
            UserSimilarity.objects.filter(
                Q(user1=target_user) | Q(user2=target_user)
            ).delete()
            
            for i, other_user in enumerate(other_users):
                if i % batch_size == 0:
                    print(f"   Progress: {i}/{total_users}")
                
                # Calculate similarity
                sim_data = self.calculate_similarity_between_users(
                    target_user, other_user
                )
                
                # Save only if above threshold
                if sim_data['combined_similarity'] >= self.min_similarity_threshold:
                    user1, user2 = (target_user, other_user) if target_user.id < other_user.id else (other_user, target_user)
                    
                    UserSimilarity.objects.create(
                        user1=user1,
                        user2=user2,
                        **sim_data
                    )
                    similarities_created += 1
        
        print(f"Created {similarities_created} user similarity records")
        return similarities_created
    
    def calculate_all_similarities(self, batch_size=50):
        """
        Calculate similarities for all users
        """
        print("CALCULATING ALL USER SIMILARITIES")
        print("=" * 50)
        
        # Get users with reviews or profiles
        users = User.objects.filter(
            models.Q(reviews__isnull=False) | 
            models.Q(preference_profile__isnull=False)
        ).distinct()
        
        total_users = users.count()
        print(f"👥 Processing {total_users} users...")
        
        processed = 0
        total_similarities = 0
        
        for user in users:
            try:
                count = self.calculate_similarities_for_user(user, batch_size)
                total_similarities += count
                processed += 1
                
                if processed % 10 == 0:
                    print(f"Progress: {processed}/{total_users} users")
            
            except Exception as e:
                print(f"Error processing {user.username}: {e}")
                continue
        
        print("=" * 50)
        print(f"✅ USER SIMILARITY CALCULATION COMPLETED!")
        print(f"👥 Users processed: {processed}/{total_users}")
        print(f"🔗 Total similarities: {total_similarities}")
        
        return total_similarities
    
    def get_collaborative_recommendations(self, user, limit=10, min_similarity=0.3):
        """
        Get book recommendations based on similar users (collaborative filtering)
        """
        # Find similar users
        similar_users = UserSimilarity.get_similar_users(
            user, 
            limit=20,  # Get more similar users
            min_similarity=min_similarity
        )
        
        if not similar_users:
            return []
        
        # Get books rated highly by similar users
        from ..models import Book
        
        # Books already reviewed by target user
        reviewed_book_ids = set(
            BookReview.objects.filter(user=user).values_list('book_id', flat=True)
        )
        
        # Collect recommendations with scores
        recommendations = defaultdict(float)
        
        for sim_data in similar_users:
            similar_user = sim_data['user']
            similarity = sim_data['similarity']
            
            # Get their highly rated books
            high_ratings = BookReview.objects.filter(
                user=similar_user,
                rating__gte=7  # Only books rated 7+
            ).exclude(
                book_id__in=reviewed_book_ids
            ).select_related('book')
            
            for review in high_ratings:
                # Weight by similarity and rating
                score = similarity * (review.rating / 10.0)
                recommendations[review.book] += score
        
        # Sort by score
        sorted_recommendations = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        # Format results
        results = []
        for book, score in sorted_recommendations:
            results.append({
                'book': book,
                'recommendation_score': score,
                'recommendation_type': 'collaborative_filtering',
                'reason': 'Users with similar taste loved this book'
            })
        
        return results

# Singleton instance
_user_similarity_service = None

def get_user_similarity_service():
    """Get singleton instance"""
    global _user_similarity_service
    if _user_similarity_service is None:
        print("Initializing UserSimilarityService...")
        _user_similarity_service = UserSimilarityService()
        print("UserSimilarityService ready!")
    return _user_similarity_service