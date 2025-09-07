from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from .models import Tweet, Like, Dislike, Comment
from .forms import TweetForm, UserRegistrationForm, CommentForm
from .models import Profile
User = get_user_model()
def tweet_list(request):
    tweets = Tweet.objects.all().order_by('-created_at')
    return render(request, 'tweet_list.html', {
        'tweets': tweets,
        'comment_form': CommentForm()
    })
@login_required
def tweet_create(request):
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm()
    return render(request, 'tweet_form.html', {'form': form})
@login_required
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            form.save()
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_form.html', {'form': form})
@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == "POST":
        tweet.delete()
        return redirect('tweet_list')
    return render(request, 'tweet_confirm_delete.html', {'tweet': tweet})
@login_required
def like_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    Dislike.objects.filter(tweet=tweet, user=request.user).delete()
    like, created = Like.objects.get_or_create(tweet=tweet, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({
        "liked": liked,
        "likes": tweet.total_likes(),
        "dislikes": tweet.total_dislikes(),
        "user": request.user.username
    })
@login_required
def dislike_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    Like.objects.filter(tweet=tweet, user=request.user).delete()
    dislike, created = Dislike.objects.get_or_create(tweet=tweet, user=request.user)
    if not created:
        dislike.delete()
        disliked = False
    else:
        disliked = True
    return JsonResponse({
        "disliked": disliked,
        "likes": tweet.total_likes(),
        "dislikes": tweet.total_dislikes(),
        "user": request.user.username
    })
@login_required
def add_comment(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.tweet = tweet
            comment.save()
            return JsonResponse({
                "user": comment.user.username,
                "body": comment.body,
                "created_at": comment.created_at.isoformat(),
            })
    return redirect("tweet_list")
@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, user=request.user)
    if request.method == "POST":
        comment.delete()
        return JsonResponse({'deleted': True})
    return JsonResponse({'deleted': False}, status=400)
@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, user=request.user)
    if request.method != "POST":
        return JsonResponse({'error': 'POST required'}, status=400)
    new_body = request.POST.get('body')
    if not new_body:
        return JsonResponse({'error': 'body required'}, status=400)
    comment.body = new_body
    comment.save()
    return JsonResponse({
        'id': comment.id,
        'user': comment.user.username,
        'body': comment.body,
        'created_at': comment.created_at.isoformat()
    })
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            # save account in session for switching later
            _store_account_in_session(request, user)
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            _store_account_in_session(request, user)
            return redirect('tweet_list')
    return render(request, 'registration/login.html')
@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')
def _store_account_in_session(request, user):
    """Helper: store multiple accounts in session"""
    if "accounts" not in request.session:
        request.session["accounts"] = []
    if user.username not in request.session["accounts"]:
        request.session["accounts"].append(user.username)
    request.session.modified = True
@login_required
def switch_account(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    request.session['active_profile_id'] = profile.id
    return redirect('tweet_list')
def add_account(request):
    if request.method == "POST":
        username = request.POST.get("username")
        bio = request.POST.get("bio")
        print("New account:", username, bio)
        messages.success(request, f"Account {username} added successfully!")
        return redirect("add_account")  # reload page after submit
    return render(request, "accounts/add_account.html")
def search_view(request):
    query = request.GET.get('q', '')
    results = Tweet.objects.filter(
        Q(text__icontains=query) | Q(user__username__icontains=query)
    ) if query else []
    return render(request, 'tweet/search_results.html', {
        'query': query,
        'results': results
    })
