from django.shortcuts import render
from post_management.models import NewsPost, VideoNews
from django.template import loader
from django.http import HttpResponse
from django.utils.http import http_date
from django.utils import timezone
from datetime import datetime, timedelta
import calendar

def auto_refresh_response(template_name, context, request):
    response = HttpResponse(loader.get_template(template_name).render(context), content_type='application/xml')

    expiry_time = datetime.utcnow() + timedelta(seconds=300)
    response["Expires"] = http_date(expiry_time.timestamp())
    response["Cache-Control"] = "max-age=0, no-cache, no-store, must-revalidate"
    response["Pragma"] = "no-cache"

    if "_refresh" not in request.GET:
        refresh_url = request.build_absolute_uri() + ("&_refresh=true" if "?" in request.build_absolute_uri() else "?_refresh=true")
        response["Refresh"] = f"600; url={refresh_url}" 

    return response

# 📌 Custom Sitemap Index
def custom_sitemap_index(request):
    """Generate Custom Sitemap Index with Auto Refresh and SEO-Friendly Headers"""
    now = timezone.now().strftime('%Y-%m-%dT%H:%M:%SZ')

    sitemaps = [
        {'loc': 'https://www.armustnews.com/sitemap/news', 'lastmod': now},
        {'loc': 'https://www.armustnews.com/sitemap/videos', 'lastmod': now},
        {'loc': 'https://www.armustnews.com/sitemap/articles', 'lastmod': now},
        {'loc': 'https://www.armustnews.com/sitemap/images', 'lastmod': now},
        {'loc': 'https://www.armustnews.com/sitemap/archive', 'lastmod': now},
    ]

    return auto_refresh_response('sitemap_index.xml', {'sitemaps': sitemaps}, request)

# 📰 News Sitemap
def sitemap_news(request):
    """Generate News Sitemap with Auto Refresh"""
    five_days_ago = timezone.now() - timedelta(days=7)
    news_items = NewsPost.objects.filter(status="active", post_date__gte=five_days_ago).order_by('-updated_at')

    processed_news_items = [
        {
            'loc': f"https://www.armustnews.com{item.get_absolute_url()}",
            'lastmod': item.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'publication_name': 'armustnews',
            'language': 'en',
            'publication_date': item.post_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'title': item.post_title
        }
        for item in news_items
    ]

    return auto_refresh_response('sitemap_news.xml', {'news_items': processed_news_items}, request)

# 🖼️ Image Sitemap
def sitemap_images(request):
    """Generate an Image Sitemap Index with Auto Refresh"""
    image_posts = NewsPost.objects.filter(post_image__isnull=False).order_by('-updated_at')

    sitemap_entries = {}
    for post in image_posts:
        year_month = post.post_date.strftime("%Y/%m")
        if year_month not in sitemap_entries:
            sitemap_entries[year_month] = post.post_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    sitemap_list = [{'loc': f"https://www.armustnews.com/sitemap/images/{key}", 'lastmod': value} for key, value in sitemap_entries.items()]

    return auto_refresh_response('sitemap_images.xml', {'sitemaps': sitemap_list}, request)

# 📅 Image Sitemap by Month
def sitemap_images_by_month(request, year, month):
    """Generate Image Sitemap for a specific month (YYYY/MM)"""
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = datetime(year, month, calendar.monthrange(year, month)[1])

    image_posts = NewsPost.objects.filter(post_image__isnull=False, post_date__gte=first_day_of_month, post_date__lte=last_day_of_month).order_by('-updated_at')

    sitemap_entries = [
        {
            'loc': f"https://www.armustnews.com{post.get_absolute_url()}",
            'image': f"https://www.armustnews.com{post.post_image.url}",
            'lastmod': post.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        for post in image_posts
    ]

    return auto_refresh_response('sitemap_images_by_month.xml', {'sitemaps': sitemap_entries}, request)

# 🎥 Video Sitemap
def sitemap_videos(request):
    """Generate a Video Sitemap Index grouped by year/month"""
    video_posts = VideoNews.objects.filter(is_active="active").order_by('-updated_at')

    sitemap_entries = {}
    for post in video_posts:
        year_month = post.video_date.strftime("%Y/%m")
        if year_month not in sitemap_entries:
            sitemap_entries[year_month] = post.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')

    sitemap_list = [{'loc': f"https://www.armustnews.com/sitemap/videos/{key}", 'lastmod': value} for key, value in sitemap_entries.items()]

    return auto_refresh_response('sitemap_video.xml', {'sitemaps': sitemap_list}, request)

# 📅 Video Sitemap by Month
def sitemap_videos_by_month(request, year, month):
    """Generate Video Sitemap for a specific month (YYYY/MM)"""
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = datetime(year, month, calendar.monthrange(year, month)[1])

    video_posts = VideoNews.objects.filter(is_active="active", video_date__gte=first_day_of_month, video_date__lte=last_day_of_month).order_by('-updated_at')

    sitemap_entries = [
        {
            'loc': f"https://www.armustnews.com{post.get_absolute_url()}",
            'video': post.video_url,
            'video_type': post.video_type,
            'video_short_des': post.video_short_des,
            'thumbnail': f"https://www.armustnews.com{post.video_thumbnail.url}" if post.video_thumbnail else "",
            'lastmod': post.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'title': post.video_title,
            'viewcounter': post.viewcounter,
            'publish_date': post.video_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        for post in video_posts
    ]

    return auto_refresh_response('sitemap_videos_by_month.xml', {'sitemaps': sitemap_entries}, request)

# 📖 Article Sitemap
def sitemap_article(request):
    """Generate an Article Sitemap Index grouped by year/month"""
    article_posts = NewsPost.objects.filter(status="active", articles=True).order_by('-updated_at')

    sitemap_entries = {}
    for post in article_posts:
        year_month = post.post_date.strftime("%Y/%m")
        if year_month not in sitemap_entries:
            sitemap_entries[year_month] = post.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')

    sitemap_list = [{'loc': f"https://www.armustnews.com/sitemap/articles/{key}", 'lastmod': value} for key, value in sitemap_entries.items()]

    return auto_refresh_response('sitemap_article.xml', {'sitemaps': sitemap_list}, request)


def sitemap_article_by_month(request, year, month):
    """Generate Article Sitemap for a specific month (YYYY/MM)"""
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = datetime(year, month, calendar.monthrange(year, month)[1])

    article_posts = NewsPost.objects.filter(
        status="active",
        articles=True,
        post_date__gte=first_day_of_month,
        post_date__lte=last_day_of_month
    ).order_by('-updated_at')

    sitemap_entries = [
        {
            'loc': f"https://www.armustnews.com{post.get_absolute_url()}",
            'lastmod': post.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'title': post.post_title,
            'publish_date': post.post_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        for post in article_posts
    ]

    return auto_refresh_response('sitemap_article_by_month.xml', {'sitemaps': sitemap_entries}, request)

# 🗂️ Archive Sitemap
def sitemap_archive(request):
    """Generate an Archive Sitemap Index grouped by year/month"""
    archive_posts = NewsPost.objects.filter(status="active").order_by('-updated_at')

    sitemap_entries = {}
    for post in archive_posts:
        year_month = post.post_date.strftime("%Y/%m")
        if year_month not in sitemap_entries:
            sitemap_entries[year_month] = post.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ')

    sitemap_list = [{'loc': f"https://www.armustnews.com/sitemap/archive/{key}", 'lastmod': value} for key, value in sitemap_entries.items()]

    return auto_refresh_response('sitemap_archive.xml', {'sitemaps': sitemap_list}, request)

# 📅 Archive Sitemap by Month
def sitemap_archive_by_month(request, year, month):
    """Generate Archive Sitemap for a specific month (YYYY/MM)"""
    first_day_of_month = datetime(year, month, 1)
    last_day_of_month = datetime(year, month, calendar.monthrange(year, month)[1])

    archive_posts = NewsPost.objects.filter(
        status="active",
        post_date__gte=first_day_of_month,
        post_date__lte=last_day_of_month
    ).order_by('-updated_at')

    sitemap_entries = [
        {
            'loc': f"https://www.armustnews.com{post.get_absolute_url()}",
            'lastmod': post.updated_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'title': post.post_title,
            'publish_date': post.post_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
        for post in archive_posts
    ]

    return auto_refresh_response('sitemap_archive_by_month.xml', {'sitemaps': sitemap_entries}, request)
