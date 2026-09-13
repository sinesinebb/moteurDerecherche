# -*- coding: utf-8 -*-

from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy.utils.project import get_project_settings
from crawling.items import RawResponseItem
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging
import re
import PyPDF2
import docx
import openpyxl
from pptx import Presentation
from io import BytesIO
import boto3
from botocore.client import Config
from scrapy_redis.connection import get_redis_from_settings
from w3lib.url import canonicalize_url


class ThematicInfoSpider(RedisCrawlSpider):
    name = "infoscraper"
    redis_key = "sc:start_urls"

    # 🚀 BOOST : domaines techniques supplémentaires
    allowed_domains = [
        "stackoverflow.com", "github.com", "dev.to", "realpython.com", "css-tricks.com",
        "docs.python.org", "reactjs.org", "vuejs.org",
        "nodejs.org", "digitalocean.com", "freecodecamp.org", "web.dev",
        "lemondeinformatique.fr", "developpez.com", "openclassrooms.com", "grafikart.fr",
        "cfi-ciras.cg", "ciras.cg", "elastic.co", "istio.io", "apache.org", "kubernetes.io",
        "docker.com", "nginx.org", "python.org", "rfc-editor.org", "jetbrains.com",
        "atom.io", "princeton.edu", "mit.edu", "coursera.org", "edx.org",
        "manning.com", "apress.com", "oreilly.com", "twilio.com", "google.com",
        "microsoft.com", "aws.amazon.com", "azure.com",
        "postgresql.org", "mysql.com", "mongodb.com", "redis.io", "kafka.apache.org",
        "zookeeper.apache.org", "traefik.io", "consul.io", "vaultproject.io",
        "hashicorp.com", "jenkins.io", "gitlab.com", "github.com", "bitbucket.org",
        "atlassian.com", "gnu.org", "llvm.org", "boost.org", "opencv.org",
        "pytorch.org", "tensorflow.org", "huggingface.co", "spacy.io", "nltk.org",
        "scipy.org", "numpy.org", "pandas.pydata.org", "matplotlib.org", "developer.mozilla.org",
        "scikit-learn.org", "keras.io", "fast.ai", "deeplearning.ai", "openai.com", "wikipedia.org",
        # 🚀 BOOST : nouveaux domaines très techniques
        "spring.io", "fastapi.tiangolo.com", "graphql.org", "sqlite.org", "mariadb.org",
        "cassandra.apache.org", "cockroachlabs.com", "nginx.com", "haproxy.org",
        "envoyproxy.io", "linkerd.io", "openpolicyagent.org", "spiffe.io",
        "terraform.io", "ansible.com", "pulumi.com", "argoproj.github.io",
        "kyverno.io", "trivy.dev", "neuvector.com", "aquasec.com",
        "snyk.io", "sonarqube.org", "codacy.com", "coveralls.io",
        "codeclimate.com", "circleci.com", "travis-ci.org", "drone.io",
        "octopus.com", "spinnaker.io", "fluxcd.io", "tekton.dev",
        "backstage.io", "kiali.io", "jaegertracing.io", "opentelemetry.io",
        "newrelic.com", "datadoghq.com", "dynatrace.com", "appdynamics.com",
        "splunk.com", "sumologic.com", "elastic.co", "graylog.org",
        "fluentd.org", "vector.dev", "logz.io", "humio.com",
        "coralogix.com", "logdna.com", "papertrail.com", "rollbar.com",
        "bugsnag.com", "honeybadger.io", "airbrake.io", "raygun.com",
        "instana.com", "lightstep.com", "thousandeyes.com", "catchpoint.com",
        "pingdom.com", "statuscake.com", "uptimerobot.com", "betterstack.com",
        "signalfx.com", "chronosphere.io", "grafana.com", "prometheus.io",
        "influxdata.com", "timescale.com", "questdb.io", "griddb.net",
        "yugabyte.com", "scylladb.com", "arangodb.com", "dgraph.io",
        "neo4j.com", "tigergraph.com", "janusgraph.org", "orientdb.org",
        "datastax.com", "couchbase.com", "memcached.org", "etcd.io",
        "consul.io", "nomadproject.io", "vaultproject.io", "boundaryproject.io",
        "waypointproject.io", "packer.io", "vagrantup.com", "serf.io",
        "otto-project.io", "levant.io",
    ]

    rules = (
        Rule(
            LinkExtractor(
                allow=(r'\.html$', r'\.php$',
                       r'/(article|news|docs|tutorial|guide|blog|post|page|course|document|library|reference|howto|topic|learn|handbook|spec)/'),
                deny=(
                    r'/login($|/|\?)', r'/signup($|/|\?)', r'/account($|/|\?)',
                    r'\?return_to=', r'github\.com/login',
                    r'/tag/', r'/category/', r'/author/', r'/comments/', r'/print/',
                    r'/share/', r'/cart/', r'/checkout/', r'/payment/', r'/admin/', r'/dashboard/',
                    r'/settings', r'/profile', r'/organizations', r'/repositories',
                    r'github\.com/signup', r'github\.com/settings', r'github\.com/orgs/',
                    r'[?&](utm_|ref=|source=|campaign=|track=|session=)',  # tracking
                    r'\.(jpg|jpeg|png|gif|svg|ico)(\?|$)',                # images directes
                    r'\.(css|js|xml|json|rss|atom)(\?|$)',                # ressources statiques
                ),
                deny_extensions=["jpg", "jpeg", "png", "gif", "pdf", "js", "css", "zip", "exe", "mp4"],
            ),
            callback="parse_page",
            follow=True,
            process_links="process_links",
        ),
        Rule(
            LinkExtractor(
                # 🚀 BOOST : ajout de nouveaux formats de documents
                allow=(r'\.pdf$', r'\.docx?$', r'\.pptx?$', r'\.xlsx?$',
                       r'\.txt$', r'\.md$', r'\.odt$', r'\.ods$', r'\.odp$',
                       r'\.rtf$', r'\.epub$'),
            ),
            callback='parse_document',
            follow=False,
        ),
    )

    custom_settings = {
        # 🚀 BOOST : concurrence accrue
        "CONCURRENT_REQUESTS": 24,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 6,
        "DOWNLOAD_DELAY": 0.35,
        "DEPTH_LIMIT": 5,
        "SCHEDULER_FLUSH_ON_START": True,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 0.5,
        "AUTOTHROTTLE_MAX_DELAY": 3,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 2.5,
        "LOG_LEVEL": "INFO",
        "ITEM_PIPELINES": {
            "crawling.pipelines.KafkaPipeline": 100,
        },
        "MEDIA_ALLOW_REDIRECTS": True,
        "ROBOTSTXT_OBEY": False,
        "USER_AGENT": "Mozilla/5.0 (compatible; InfoScraper/2.0; +http://votre-projet.com/bot)",
        "COOKIES_ENABLED": False,
        "RETRY_TIMES": 3,
        "DOWNLOAD_TIMEOUT": 20,
        "DNSCACHE_ENABLED": True,
        # 🚀 BOOST : timeouts réseau plus agressifs
        "DOWNLOAD_TIMEOUT": 18,
        "DNS_TIMEOUT": 5,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = get_project_settings()
        self.logger.info(f"→ ThematicInfoSpider démarré, redis_key = {self.redis_key}")

        self.redis_server = get_redis_from_settings(self.settings)

        # 🚀 BOOST : limites par domaine relevées
        self.max_pages_per_domain = 500
        self.target_score_per_domain = 25.0

        self._domain_scores = {}

        self.keywords = [
            "programmation", "programming", "python", "java", "javascript", "nodejs",
            "golang", "rust", "c++", "linux", "ubuntu", "docker", "kubernetes",
            "cloud", "aws", "azure", "gcp", "data", "machine learning", "deep learning",
            "cybersécurité", "security", "api", "database", "sql", "nosql", "react",
            "vue", "angular", "django", "flask", "pytorch", "tensorflow", "C#", "data science", "REST", "ciras",
            "typescript", "kotlin", "swift", "scala", "r", "matlab", "julia",
            "hadoop", "spark", "flink", "storm", "kafka", "rabbitmq",
            "ci/cd", "devops", "git", "github", "gitlab", "bitbucket",
            "microservices", "serverless", "lambda", "api gateway",
            "terraform", "ansible", "chef", "puppet", "saltstack",
            "prometheus", "grafana", "elasticsearch", "kibana", "logstash",
            "nginx", "apache", "haproxy", "envoy", "traefik",
            "openstack", "vmware", "virtualbox", "vagrant",
            "jupyter", "numpy", "scipy", "pandas", "scikit-learn",
            "matplotlib", "seaborn", "plotly", "bokeh",
            "tidyverse", "ggplot2", "shiny", "rstudio",
        ]
        self.keyword_weights = {
            k: 2.0 if k in ("python", "programming", "docker", "kubernetes", "cloud", "machine learning", "deep learning", "devops")
            else 1.0 for k in self.keywords
        }

    # ----------------------------------------------------------------------
    # Gestion du crawl par domaine (compteurs Redis + score cumulé)
    # ----------------------------------------------------------------------
    def get_domain_count(self, domain):
        key = f"crawled:{domain}:count"
        return int(self.redis_server.get(key) or 0)

    def increment_domain_count(self, domain):
        key = f"crawled:{domain}:count"
        self.redis_server.incr(key)
        self.redis_server.expire(key, 86400)

    def get_domain_score(self, domain):
        if domain not in self._domain_scores:
            key = f"crawled:{domain}:score"
            val = self.redis_server.get(key)
            self._domain_scores[domain] = float(val) if val else 0.0
        return self._domain_scores[domain]

    def add_domain_score(self, domain, score):
        current = self.get_domain_score(domain)
        new_score = current + score
        key = f"crawled:{domain}:score"
        self.redis_server.set(key, new_score)
        self.redis_server.expire(key, 86400)
        self._domain_scores[domain] = new_score

    def should_follow_domain(self, domain):
        if self.get_domain_count(domain) >= self.max_pages_per_domain:
            self.logger.debug(f"Domaine {domain} atteint la limite de pages ({self.max_pages_per_domain})")
            return False
        if self.get_domain_score(domain) >= self.target_score_per_domain:
            self.logger.debug(f"Domaine {domain} a atteint le score cible ({self.target_score_per_domain})")
            return False
        return True

    # ----------------------------------------------------------------------
    # Filtrage intelligent des liens à suivre
    # ----------------------------------------------------------------------
    def process_links(self, links):
        """
        Appelé automatiquement par la Rule pour filtrer les liens extraits.
        On en profite pour :
          - canoniser les URLs (suppression paramètres inutiles, fragments)
          - supprimer les doublons
          - ignorer les liens de pagination, calendriers, archives
          - arrêter de suivre un domaine qui a atteint ses limites
        """
        filtered = []
        seen_urls = set()

        for link in links:
            clean_url = canonicalize_url(link.url)
            if clean_url in seen_urls:
                continue
            seen_urls.add(clean_url)
            link.url = clean_url

            domain = urlparse(clean_url).netloc
            if not domain:
                continue

            if not self.should_follow_domain(domain):
                continue

            url_low = clean_url.lower()

            # Pièges : captcha, login, sessions, etc.
            if any(x in url_low for x in ['/login', '/signin', '/signup', '/captcha', '/auth',
                                           '/register', '/logout', '/session', '/verify',
                                           '/security', '/recover', '/reset-password']):
                continue

            # 🚀 BOOST : ignorer les URLs de recherche interne
            if re.search(r'[?&](page|p|sort|order|search|query|q|keyword)=', url_low):
                continue
            if re.search(r'/\d{4}/\d{2}/', url_low):
                continue
            if re.search(r'/(tag|category|author|archives)/', url_low):
                continue

            # Fichiers statiques ou images directes
            if re.search(r'\.(jpg|jpeg|png|gif|webp|svg|bmp|ico)(\?|$)', url_low):
                continue
            if re.search(r'\.(mp4|webm|ogg|avi|mkv)(\?|$)', url_low):
                continue

            if 'youtube.com' in domain and re.search(r'/(c|user)/', url_low):
                continue

            filtered.append(link)

        return filtered

    # ----------------------------------------------------------------------
    # Extraction des infos YouTube (conservée pour compatibilité)
    # ----------------------------------------------------------------------
    def extract_youtube_info(self, url):
        patterns = [
            r'(?:youtube\.com/(?:watch\?v=|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})',
        ]
        for pat in patterns:
            m = re.search(pat, url)
            if m:
                vid = m.group(1)
                return {
                    "video_id": vid,
                    "watch_url": f"https://www.youtube.com/watch?v={vid}",
                    "embed_url": f"https://www.youtube.com/embed/{vid}",
                    "thumbnail": f"https://img.youtube.com/vi/{vid}/hqdefault.jpg",
                    "platform": "youtube",
                    "type": "youtube"
                }
        return None

    def is_valid_media_url(self, url, media_type='image'):
        if not url:
            return False
        u = url.strip()
        u = u.split('?')[0].split('#')[0]
        if not u:
            return False
        if not u.startswith(('http://', 'https://', '//')) and not u.startswith('/'):
            return False
        if media_type == 'image':
            if any(u.lower().endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico')):
                return True
            if any(kw in u.lower() for kw in ['image', 'img', 'photo', 'thumb', 'logo', 'icon', 'sprite']):
                return True
            return False
        if media_type == 'video':
            return any(u.lower().endswith(ext) for ext in ('.mp4', '.webm', '.ogg')) or 'youtube' in u or 'youtu.be' in u
        return False

    def extract_media_urls(self, response):
        images = []
        videos = []
        for img in response.css('img'):
            for attr in ('src', 'data-src', 'data-original', 'data-lazy-src', 'data-srcset'):
                url = img.attrib.get(attr)
                if url:
                    full = urljoin(response.url, url)
                    if self.is_valid_media_url(full, 'image') and not any(img['url'] == full for img in images):
                        alt = img.attrib.get('alt', '')
                        title = img.attrib.get('title', '')
                        images.append({
                            'url': full,
                            'alt': alt,
                            'title': title
                        })
                        break
        for iframe in response.css('iframe[src*="youtube"], iframe[src*="youtu.be"]'):
            src = iframe.attrib.get('src')
            if src:
                info = self.extract_youtube_info(src)
                if info:
                    videos.append(info)
        for a in response.css('a[href]'):
            href = a.attrib.get('href')
            if href and self.is_valid_media_url(href, 'video'):
                full = urljoin(response.url, href)
                videos.append({"video_url": full, "type": "direct", "platform": "direct"})
        return images, videos

    # ----------------------------------------------------------------------
    # Extraction de contenu textuel (améliorée)
    # ----------------------------------------------------------------------
    def extract_text_content(self, response, max_chars=15000):
        selectors = [
            'article', 'main', '[role="main"]', '.article-content', '.post-content',
            '.entry-content', '.content', '.docs-content', '.tutorial-content', '#content'
        ]
        best_text = ""
        for sel in selectors:
            nodes = response.css(sel)
            if not nodes:
                continue
            text_parts = []
            for n in nodes:
                # 🚀 BOOST : éliminer les scripts et styles inline
                for script in n.css('script, style, noscript'):
                    script.extract()
                parts = n.xpath('.//text()').getall()
                if parts:
                    cleaned = " ".join(p.strip() for p in parts if p and p.strip())
                    if cleaned:
                        text_parts.append(cleaned)
            candidate = " ".join(text_parts).strip()
            if len(candidate) > len(best_text):
                best_text = candidate
        if not best_text:
            body = response.xpath('//body//text()').getall()
            best_text = " ".join(p.strip() for p in body if p and p.strip())
        best_text = re.sub(r'\s+', ' ', best_text).strip()
        return best_text[:max_chars]

    def thematic_score(self, text, url):
        score = 0.0
        tl = text.lower()
        for kw, w in self.keyword_weights.items():
            if kw in tl:
                score += w
        # 🚀 BOOST : bonus pour des patterns d’URL très techniques
        if any(kw in url.lower() for kw in ("python", "docker", "kubernetes", "cloud", "aws", "azure",
                                             "machine", "data", "ml", "c++", "java", "javascript",
                                             "c#", "c", "sql", "html", "ia", "db", "frontend", "backend",
                                             "css", "uml", "cybersécurité", "api", "graphql", "serverless",
                                             "microservices", "devops", "sre", "observability")):
            score += 2.0
        return score

    # ----------------------------------------------------------------------
    # Extraction des documents (PDF, DOCX, etc.) – inchangée
    # ----------------------------------------------------------------------
    def extract_pdf_text(self, data):
        try:
            pdf = PyPDF2.PdfReader(BytesIO(data))
            return '\n'.join(page.extract_text() for page in pdf.pages)
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {e}")
            return ''

    def extract_docx_text(self, data):
        try:
            doc = docx.Document(BytesIO(data))
            return '\n'.join(para.text for para in doc.paragraphs)
        except Exception as e:
            self.logger.error(f"DOCX extraction failed: {e}")
            return ''

    def extract_pptx_text(self, data):
        try:
            prs = Presentation(BytesIO(data))
            texts = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, 'text'):
                        texts.append(shape.text)
            return '\n'.join(texts)
        except Exception as e:
            self.logger.error(f"PPTX extraction failed: {e}")
            return ''

    def extract_xlsx_text(self, data):
        try:
            wb = openpyxl.load_workbook(BytesIO(data), data_only=True)
            texts = []
            for sheet in wb.sheetnames:
                ws = wb[sheet]
                for row in ws.iter_rows(values_only=True):
                    texts.extend(str(cell) for cell in row if cell)
            return '\n'.join(texts)
        except Exception as e:
            self.logger.error(f"XLSX extraction failed: {e}")
            return ''

    def count_pdf_pages(self, data):
        try:
            pdf = PyPDF2.PdfReader(BytesIO(data))
            return len(pdf.pages)
        except:
            return 0

    def count_docx_pages(self, data):
        try:
            doc = docx.Document(BytesIO(data))
            return max(1, len(doc.paragraphs) // 20)
        except:
            return 0

    def count_pptx_slides(self, data):
        try:
            prs = Presentation(BytesIO(data))
            return len(prs.slides)
        except:
            return 0

    # ----------------------------------------------------------------------
    # Parsing principal
    # ----------------------------------------------------------------------
    def parse_start_url(self, response):
        if response.url.lower().endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
                                          '.txt', '.md', '.odt', '.ods', '.odp', '.rtf', '.epub')):
            return self.parse_document(response)
        else:
            return self.parse_page(response)

    def parse_page(self, response):
        if response.status in (403, 429):
            self.logger.warning(f"Accès bloqué ou limité sur {response.url}")
            return

        content_type_header = response.headers.get("Content-Type", b"").decode(errors='ignore')
        if "text/html" not in content_type_header.lower():
            self.logger.debug(f"Skip non-html: {response.url} ({content_type_header})")
            return
        
            # Rejeter explicitement les URLs de login / auth (y compris les redirections)
        if any(x in response.url.lower() for x in ['/login', '/signin', '/signup', '/auth', '/session', '/verify', '/recover', '/reset-password']):
            self.logger.info(f"Page d'authentification détectée par URL, ignorée : {response.url}")
            return

        title = response.css('title::text').get(default="").strip()
        title_lower = title.lower()

        if any(x in title_lower for x in ['captcha', 'login', 'sign in', 'access denied', 'just a moment']):
            self.logger.info(f"Page de blocage détectée, ignorée: {response.url}")
            return

        # Détection renforcée : contenu de la page
        if re.search(r'captcha|verify you are a human|are you a robot|please prove you are not a robot', response.text, re.I):
            self.logger.info(f"Page avec captcha détectée, ignorée : {response.url}")
            return

        if 'youtube.com' in response.url and (
            '404 not found' in title_lower or
            'this page isn\'t available' in title_lower or
            'video unavailable' in response.text.lower() or
            'this video is private' in response.text.lower() or
            'this video has been removed' in response.text.lower()
        ):
            self.logger.info(f"Page YouTube invalide, ignorée : {response.url}")
            return

        self.logger.info(f"Crawling page: {response.url}")

        try:
            images, video_info_list = self.extract_media_urls(response)
            extracted_text = self.extract_text_content(response)
            description = response.css('meta[name="description"]::attr(content)').get(default='').strip()

            parsed_url = urlparse(response.url)
            if 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc:
                if re.search(r'(watch\?v=|/shorts/|/live/)', response.url):
                    if not video_info_list:
                        match = re.search(r'(?:watch\?v=|/shorts/|/live/)([A-Za-z0-9_-]{11})', response.url)
                        if match:
                            vid = match.group(1)
                            video_info_list.append({
                                "video_id": vid,
                                "watch_url": f"https://www.youtube.com/watch?v={vid}",
                                "embed_url": f"https://www.youtube.com/embed/{vid}",
                                "thumbnail": f"https://img.youtube.com/vi/{vid}/hqdefault.jpg",
                                "platform": "youtube",
                                "type": "youtube"
                            })

            youtube_ids = []
            for v in video_info_list:
                if v.get("video_id"):
                    youtube_ids.append(v["video_id"])
            if not youtube_ids and 'youtube.com' in response.url:
                match = re.search(r'(?:watch\?v=|/shorts/|/live/)([A-Za-z0-9_-]{11})', response.url)
                if match:
                    youtube_ids.append(match.group(1))

            score = self.thematic_score(extracted_text, response.url)
            media_count = len(images) + len(video_info_list)
            is_thematic = (score >= 1.5) or ("tutorial" in response.url.lower() or "guide" in response.url.lower())

            programming_languages = []
            technical_concepts = []
            has_code_examples = False
            has_shell_commands = False

            text_lower = extracted_text.lower()
            for kw in self.keywords:
                if kw in text_lower:
                    if kw in ["python", "java", "javascript", "c++", "c#", "php", "ruby", "go", "rust", "swift",
                              "typescript", "html", "css", "sql", "bash", "shell", "powershell", "dockerfile",
                              "kotlin", "scala", "r", "matlab", "julia"]:
                        programming_languages.append(kw)
                    else:
                        technical_concepts.append(kw)

            if re.search(r'```|~~~|<code>|<pre>', response.text):
                has_code_examples = True

            # 🚀 BOOST : détection plus fine des commandes shell
            if re.search(r'^\s*[\$\#\>]\s+\w+', response.text, re.MULTILINE):
                has_shell_commands = True
            if re.search(r'\bcurl\b|\bwget\b|\bgpg\b|\bgit\b|\bdocker\b|\bkubectl\b', response.text, re.I):
                has_shell_commands = True

            difficulty_level = "intermediate"
            url_lower = response.url.lower()
            if "beginner" in url_lower or "debutant" in url_lower or "tutorial" in url_lower or "intro" in title_lower:
                difficulty_level = "beginner"
            elif "advanced" in url_lower or "expert" in url_lower or "deep" in url_lower or "avancé" in title_lower:
                difficulty_level = "advanced"

            technical_metadata = {
                "programming_languages": list(set(programming_languages)),
                "technical_concepts": list(set(technical_concepts)),
                "difficulty_level": difficulty_level,
                "has_code_examples": has_code_examples,
                "has_shell_commands": has_shell_commands
            }

            item = RawResponseItem()
            item["appid"] = self.settings.get("SPIDER_ID", "default")
            item["crawlid"] = self.name
            item["url"] = response.url
            item["response_url"] = response.url
            item["status_code"] = response.status
            item["response_headers"] = {k.decode(): [v_.decode() for v_ in v] for k, v in response.headers.items()}
            item["request_headers"] = {k.decode(): [v_.decode() for v_ in v] for k, v in response.request.headers.items()}
            item["body"] = response.text
            item["encoding"] = response.encoding
            item["title"] = title
            item["description"] = description
            item["keywords_found"] = [kw for kw in self.keywords if kw in text_lower]
            item["image_urls"] = [img['url'] for img in images]
            video_urls = []
            for v in video_info_list:
                for key in ("watch_url", "embed_url", "video_url"):
                    if v.get(key):
                        if v.get(key) not in video_urls:
                            video_urls.append(v.get(key))
                        break
            item["video_urls"] = video_urls
            item["media_count"] = media_count
            item["images_count"] = len(images)
            item["videos_count"] = len(video_urls)
            item["youtube_videos_count"] = len([v for v in video_info_list if v.get("type") == "youtube"])
            item["content"] = extracted_text
            item["metadata"] = {
                "source": response.url,
                "title": item["title"],
                "appid": self.settings.get("SPIDER_ID", "default")
            }
            item["technical_metadata"] = technical_metadata

            if item["youtube_videos_count"] > 0:
                item["content_type"] = "youtube_video"
            elif video_urls:
                item["content_type"] = "video"
            elif len(images) > 3:
                item["content_type"] = "image"
            else:
                item["content_type"] = "web"

            item["extracted_content"] = extracted_text
            item["crawled_at"] = datetime.utcnow().isoformat()
            parsed = urlparse(response.url)
            item["domain"] = parsed.netloc
            item["path"] = parsed.path.lstrip('/')
            item["thematic_score"] = score
            item["is_thematic"] = bool(is_thematic)

            item["youtube_video_ids"] = youtube_ids

            links = []
            for a in response.css('a[href]::attr(href)'):
                href = a.get()
                if href and not href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                    absolute_url = response.urljoin(href)
                    if not absolute_url.lower().endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.webm')):
                        links.append(absolute_url)
            item["links"] = list(set(links))

            yield item

            domain = parsed.netloc
            self.increment_domain_count(domain)
            self.add_domain_score(domain, score)

            self.logger.info(f"✅ Page item yield pour {response.url} (score={score:.1f}, domaine={domain}, pages={self.get_domain_count(domain)}, score cumulé={self.get_domain_score(domain):.1f})")

        except Exception as e:
            self.logger.error(f"Erreur parse_page {response.url}: {e}", exc_info=True)

    def parse_document(self, response):
        """Traite un fichier téléchargé (PDF, DOCX, etc.) et l'upload vers Minio."""
        try:
            self.logger.info(f"Downloading document: {response.url}")

            content_type = response.headers.get('Content-Type', b'').decode().lower()
            file_extension = response.url.split('.')[-1].lower()

            text = ''
            pages = 0
            if 'pdf' in content_type or file_extension == 'pdf':
                text = self.extract_pdf_text(response.body)
                pages = self.count_pdf_pages(response.body)
            elif 'word' in content_type or file_extension in ('doc', 'docx'):
                text = self.extract_docx_text(response.body)
                pages = self.count_docx_pages(response.body)
            elif 'presentation' in content_type or file_extension in ('ppt', 'pptx', 'odp'):
                text = self.extract_pptx_text(response.body)
                pages = self.count_pptx_slides(response.body)
            elif 'spreadsheet' in content_type or file_extension in ('xls', 'xlsx', 'ods'):
                text = self.extract_xlsx_text(response.body)
                pages = len(text.split('\n')) // 30
            elif file_extension in ('txt', 'md', 'rtf', 'epub', 'odt'):
                text = response.text
                pages = len(text.split('\n')) // 30

            word_count = len(text.split())

            import os
            filename = os.path.basename(response.url)
            title = filename
            lines = text.strip().split('\n')
            for line in lines[:5]:
                if len(line) > 20 and not line.startswith('http'):
                    title = line.strip()[:100]
                    break

            # --- Upload vers Minio ---
            minio_url = None
            try:
                endpoint = self.settings.get('MINIO_ENDPOINT')
                access_key = self.settings.get('MINIO_ACCESS_KEY')
                secret_key = self.settings.get('MINIO_SECRET_KEY')
                bucket = self.settings.get('MINIO_BUCKET')
                secure = self.settings.get('MINIO_SECURE', True)
                self.logger.info(f"Minio settings: endpoint={endpoint}, bucket={bucket}")

                if endpoint and access_key and secret_key and bucket:
                    s3_client = boto3.client(
                        's3',
                        endpoint_url=endpoint,
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key,
                        config=Config(signature_version='s3v4'),
                        region_name='us-east-1'
                    )
                    import hashlib
                    obj_key = f"documents/{hashlib.md5(response.url.encode()).hexdigest()}_{filename}"
                    s3_client.put_object(
                        Bucket=bucket,
                        Key=obj_key,
                        Body=response.body,
                        ContentType=content_type
                    )
                    if secure:
                        minio_url = f"{endpoint}/{bucket}/{obj_key}"
                    else:
                        minio_url = f"{endpoint}/{bucket}/{obj_key}"
                    self.logger.info(f"Uploaded document to Minio: {minio_url}")
                else:
                    self.logger.warning("Minio settings missing, skipping upload")
            except Exception as e:
                self.logger.error(f"Failed to upload to Minio: {e}")

            item = RawResponseItem()
            item['url'] = response.url
            item['response_url'] = response.url
            item['title'] = title
            item['content'] = text
            item['extracted_content'] = text
            item['file_type'] = file_extension
            item['file_size'] = len(response.body)
            item['pages'] = pages
            item['word_count'] = word_count
            item['crawled_at'] = datetime.utcnow().isoformat()
            item['domain'] = urlparse(response.url).netloc
            item['path'] = urlparse(response.url).path.lstrip('/')
            item['metadata'] = {
                "source": response.url,
                "title": title,
                "appid": self.settings.get("SPIDER_ID", "default"),
                "minio_url": minio_url
            }
            item['thematic_score'] = 0.0
            item['is_thematic'] = False

            yield item
            self.logger.info(f"✅ Document yield: {response.url} (type: {file_extension}, size: {len(response.body)} bytes)")
        except Exception as e:
            self.logger.exception(f"Erreur lors du traitement du document {response.url}: {e}")