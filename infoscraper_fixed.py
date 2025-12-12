# File: crawling/spiders/infoscraper.py - VERSION CORRIGÉE

from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.utils.project import get_project_settings
from crawling.items import RawResponseItem
from datetime import datetime
from urllib.parse import urljoin
import logging
import re

class InfoSpider(RedisCrawlSpider):
    name = "infoscraper"
    redis_key = "sc:start_urls"

    allowed_domains = [
        # ... (gardez votre liste existante)
        "lemondeinformatique.fr", "developpez.com", "openclassrooms.com", "grafikart.fr",
        # ... (tous vos domaines)
    ]

    rules = (
        Rule(
            LinkExtractor(
                allow=(
                    r'\.html$', r'\.php$', r'/article/', r'/news/', r'/docs/', r'/documentation/', 
                    r'/tutorial/', r'/guide/', r'/howto/', r'/learn/', r'/course/', r'/blog/',
                    r'/post/', r'/page/', r'/chapter/', r'/lesson/', r'/training/', r'/resource/',
                    r'/example/', r'/demo/', r'/sample/', r'/project/', r'/walkthrough/',
                    r'/getting-started/', r'/introduction/', r'/overview/', r'/concepts/',
                    r'/reference/', r'/api/', r'/manual/', r'/handbook/', r'/cookbook/',
                    r'/patterns/', r'/best-practices/', r'/tips/', r'/tricks/', r'/cheatsheet/'
                ),
                deny=(
                    r'/tag/', r'/category/', r'/author/', r'/comments/', r'/print/', r'/share/',
                    r'/user/', r'/profile/', r'/search/', r'/login/', r'/signup/', r'/account/',
                    r'/cart/', r'/checkout/', r'/payment/', r'/admin/', r'/dashboard/', r'/settings/',
                    r'/privacy/', r'/terms/', r'/contact/', r'/about/', r'/help/', r'/support/'
                ),
                deny_extensions=["jpg", "jpeg", "png", "gif", "pdf", "js", "css", "zip", "exe", "mp4", "avi", "mov"],
            ),
            callback="parse_page",
            follow=True,
        ),
    )

    custom_settings = {
        "DEPTH_LIMIT": 3,
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 12,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 3,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 5,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 3.0,
        "LOG_LEVEL": "INFO",
        "ITEM_PIPELINES": {
            "crawling.pipelines.KafkaPipeline": 100,
        },
        "MEDIA_ALLOW_REDIRECTS": True,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = get_project_settings()
        self.logger.info(f"��� InfoSpider démarré, redis_key = {self.redis_key}")
        self.logger.info(f"��� Allowed domains: {len(self.allowed_domains)} domains configurés")
        
        self.keywords = [
            "programmation", "python", "java", "linux", "informatique", "réseau", "cybersécurité", 
            # ... (vos mots-clés)
        ]

    def extract_youtube_video_info(self, url):
        """Extrait les informations spécifiques des vidéos YouTube"""
        try:
            patterns = [
                r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
                r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    video_id = match.group(1)
                    return {
                        'video_id': video_id,
                        'embed_url': f'https://www.youtube.com/embed/{video_id}',
                        'watch_url': f'https://www.youtube.com/watch?v={video_id}',
                        'thumbnail': f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
                        'type': 'youtube',
                        'platform': 'youtube'
                    }
            return None
        except Exception as e:
            self.logger.debug(f"Erreur extraction YouTube info: {e}")
            return None

    def extract_media_urls(self, response):
        """Extrait les URLs des images et vidéos de la page"""
        
        image_urls = []
        video_info_list = []
        
        try:
            # === EXTRACTION DES IMAGES ===
            img_selectors = [
                'img[src]',
                'img[data-src]', 
                'img[data-original]',
                'img[data-lazy-src]',
                'img[data-srcset]'
            ]
            
            for selector in img_selectors:
                for img in response.css(selector):
                    for attr in ['data-src', 'data-original', 'data-lazy-src', 'src']:
                        url = img.css(f'::attr({attr})').get()
                        if url and self.is_valid_media_url(url):
                            full_url = urljoin(response.url, url.strip())
                            if full_url not in image_urls:
                                image_urls.append(full_url)
                            break
            
            # === EXTRACTION DES VIDÉOS SIMPLIFIÉE ===
            # On extrait juste les URLs, pas les structures complexes
            
            # Iframes YouTube
            youtube_iframes = response.css('iframe[src*="youtube"], iframe[src*="youtu.be"]')
            for iframe in youtube_iframes:
                src = iframe.css('::attr(src)').get()
                if src:
                    youtube_info = self.extract_youtube_video_info(src)
                    if youtube_info:
                        video_info_list.append(youtube_info)
            
            # Liens directs vers fichiers vidéo
            video_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.wmv', '.flv', '.mkv']
            for ext in video_extensions:
                links = response.css(f'a[href*="{ext}"]::attr(href)').getall()
                for url in links:
                    if self.is_valid_media_url(url, media_type='video'):
                        full_url = urljoin(response.url, url.strip())
                        video_info_list.append({
                            'video_url': full_url,
                            'embed_url': full_url,
                            'watch_url': full_url,
                            'type': 'direct',
                            'platform': 'direct'
                        })
        
        except Exception as e:
            self.logger.warning(f"Erreur lors de l'extraction des médias pour {response.url}: {e}")
        
        return image_urls, video_info_list

    def is_valid_media_url(self, url, media_type='image'):
        """Valide si une URL de média est valide"""
        if not url or not url.strip():
            return False
        
        clean_url = url.strip().split('?')[0].split('#')[0]
        
        if not clean_url.startswith(('http://', 'https://', '//')):
            return False
        
        if media_type == 'image':
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff']
            return any(clean_url.lower().endswith(ext) for ext in image_extensions)
        
        elif media_type == 'video':
            video_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.wmv', '.flv', '.mkv']
            video_platforms = ['youtube', 'youtu.be', 'vimeo', 'dailymotion']
            
            has_extension = any(clean_url.lower().endswith(ext) for ext in video_extensions)
            has_platform = any(platform in clean_url.lower() for platform in video_platforms)
            
            return has_extension or has_platform
        
        return True

    def extract_content_text(self, response):
        """Extrait le contenu textuel de la page"""
        try:
            content_selectors = [
                'article',
                'main',
                '[role="main"]',
                '.content',
                '.main-content',
                '.article-content',
                '.post-content', 
                '.entry-content',
                '.documentation-content',
                '.tutorial-content',
                '.docs-content',
                'section.main',
                '.body-content',
                '#content',
                '#main-content'
            ]
            
            content_text = ""
            
            for selector in content_selectors:
                elements = response.css(selector)
                if elements:
                    text_parts = []
                    for element in elements:
                        text = ' '.join(element.css('::text').getall())
                        if text.strip():
                            text_parts.append(text)
                    
                    if text_parts:
                        combined_text = ' '.join(text_parts)
                        if len(combined_text) > len(content_text):
                            content_text = combined_text
            
            if not content_text.strip():
                fallback_selectors = [
                    'body',
                    '.container',
                    '#main',
                    '.page-content'
                ]
                
                for selector in fallback_selectors:
                    elements = response.css(selector)
                    if elements:
                        text = ' '.join(elements.css('::text').getall())
                        if len(text) > len(content_text):
                            content_text = text
            
            content_text = re.sub(r'\s+', ' ', content_text).strip()
            return content_text[:15000] if len(content_text) > 15000 else content_text
            
        except Exception as e:
            self.logger.warning(f"Erreur extraction contenu pour {response.url}: {e}")
            return ""

    def parse_page(self, response):
        self.logger.info(f"��� Crawling page: {response.url}")
        
        content_type = response.headers.get("Content-Type", b"").decode(errors='ignore')
        if "text/html" not in content_type.lower():
            self.logger.debug(f"Skip non-HTML content: {response.url} - Content-Type: {content_type}")
            return

        try:
            # Extraire les URLs des médias
            image_urls, video_info_list = self.extract_media_urls(response)
            
            # Extraire le contenu textuel
            extracted_content = self.extract_content_text(response)

            item = RawResponseItem()
            item["appid"] = self.settings.get("SPIDER_ID", "default")
            item["crawlid"] = self.name
            item["url"] = response.url
            item["response_url"] = response.url
            item["status_code"] = response.status

            item["response_headers"] = {
                k.decode(): [v_.decode() for v_ in v]
                for k, v in response.headers.items()
            }
            item["request_headers"] = {
                k.decode(): [v_.decode() for v_ in v]
                for k, v in response.request.headers.items()
            }

            item["body"] = response.text
            item["encoding"] = response.encoding

            item["title"] = response.css('title::text').get(default="").strip() or response.xpath("//title/text()").get(default="").strip()
            item["description"] = response.css('meta[name="description"]::attr(content)').get(default="").strip()

            text_lower = response.text.lower()
            item["keywords_found"] = [
                kw for kw in self.keywords if kw in text_lower
            ]

            # MÉTADONNÉES MÉDIAS SIMPLIFIÉES
            item["image_urls"] = image_urls
            # Extraire les URLs vidéo de manière simple
            video_urls = []
            for video_info in video_info_list:
                for key in ["embed_url", "watch_url", "video_url"]:
                    if key in video_info and video_info[key]:
                        if video_info[key] not in video_urls:
                            video_urls.append(video_info[key])
                        break
            
            item["video_urls"] = video_urls
            item["media_count"] = len(image_urls) + len(video_urls)
            item["images_count"] = len(image_urls)
            item["videos_count"] = len(video_urls)
            item["crawled_at"] = datetime.now().isoformat()
            
            # Compter les vidéos YouTube
            youtube_videos = [v for v in video_info_list if v.get('type') == 'youtube']
            item["youtube_videos_count"] = len(youtube_videos)
            
            # Déterminer le type de contenu
            if youtube_videos:
                item["content_type"] = "youtube_video"
            elif video_urls:
                item["content_type"] = "video"
            elif image_urls and len(image_urls) > 2:
                item["content_type"] = "image"
            elif "tutorial" in response.url.lower() or "guide" in response.url.lower():
                item["content_type"] = "tutorial"
            elif "documentation" in response.url.lower() or "docs" in response.url.lower():
                item["content_type"] = "documentation"
            else:
                item["content_type"] = "article"
            
            item["extracted_content"] = extracted_content
            item["domain"] = response.url.split('/')[2]
            item["path"] = response.url.split('/', 3)[-1] if len(response.url.split('/')) > 3 else ""

            extractor = LinkExtractor(
                allow=(
                    r'\.html$', r'\.php$', r'/article/', r'/news/', r'/docs/', r'/documentation/', 
                    r'/tutorial/', r'/guide/', r'/howto/', r'/learn/', r'/course/', r'/blog/',
                    r'/post/', r'/page/', r'/chapter/', r'/lesson/', r'/training/', r'/resource/'
                ),
                deny=(
                    r'/tag/', r'/category/', r'/author/', r'/comments/', r'/print/', r'/share/',
                    r'/user/', r'/profile/', r'/search/', r'/login/', r'/signup/', r'/account/',
                    r'/cart/', r'/checkout/', r'/payment/', r'/admin/', r'/dashboard/', r'/settings/'
                ),
                deny_extensions=["jpg", "jpeg", "png", "gif", "pdf", "js", "css", "zip", "exe", "mp4"],
            )
            links = extractor.extract_links(response)
            item["links"] = [link.url for link in links]
            
            self.logger.info(f"✅ Page traitée: {response.url} - {len(links)} liens, {len(image_urls)} images, {len(video_urls)} vidéos, type: {item['content_type']}")
            yield item
            
        except Exception as e:
            self.logger.error(f"❌ Erreur traitement page {response.url}: {e}")
