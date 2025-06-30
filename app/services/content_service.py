import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict
import os
from datetime import datetime, timedelta
from tavily import TavilyClient

class ContentService:
    def __init__(self):
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.session = httpx.AsyncClient()
    
    async def search_content_tavily(self, interests: List[str], max_results: int = 20) -> List[Dict]:
        """Search for content using Tavily API"""
        all_articles = []
        
        for interest in interests:
            try:
                # Create search query
                query = f"{interest} technology news latest"
                
                # Search with Tavily
                results = self.tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=max_results // len(interests),
                    include_domains=["techcrunch.com", "wired.com", "arstechnica.com", "theverge.com"]
                )
                
                # Process results
                for result in results.get('results', []):
                    article = {
                        'title': result.get('title', ''),
                        'content': result.get('content', ''),
                        'url': result.get('url', ''),
                        'source': self.extract_domain(result.get('url', '')),
                        'category': interest,
                        'published_at': datetime.now() - timedelta(days=1),  # Approximate
                        'raw_content': result.get('raw_content', '')
                    }
                    all_articles.append(article)
                    
            except Exception as e:
                print(f"Error searching for {interest}: {e}")
                continue
        
        return all_articles
    
    async def scrape_article_content(self, url: str) -> Dict:
        """Scrape full article content using Beautiful Soup"""
        try:
            response = await self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract title
            title = ""
            title_tags = soup.find_all(['h1', 'h2', 'title'])
            if title_tags:
                title = title_tags[0].get_text().strip()
            
            # Extract main content
            content = ""
            content_selectors = [
                'article', '[role="main"]', '.content', '.post-content', 
                '.entry-content', '.article-body', 'main'
            ]
            
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    content = content_div.get_text().strip()
                    break
            
            # Fallback to paragraph extraction
            if not content:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs])
            
            # Extract publish date
            publish_date = None
            date_selectors = ['time', '[datetime]', '.date', '.published']
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date_text = date_elem.get('datetime') or date_elem.get_text()
                    try:
                        publish_date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                        break
                    except:
                        continue
            
            return {
                'title': title,
                'content': content[:2000],  # Limit content length
                'url': url,
                'published_at': publish_date or datetime.now(),
                'scraped_successfully': True
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {
                'title': '',
                'content': '',
                'url': url,
                'published_at': datetime.now(),
                'scraped_successfully': False
            }
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return "unknown"
    
    async def enhance_articles_with_scraping(self, articles: List[Dict]) -> List[Dict]:
        """Enhance articles with full content via scraping"""
        enhanced_articles = []
        
        # Limit concurrent requests
        semaphore = asyncio.Semaphore(5)
        
        async def scrape_single(article):
            async with semaphore:
                if len(article.get('content', '')) < 200:  # If content is too short
                    scraped = await self.scrape_article_content(article['url'])
                    if scraped['scraped_successfully']:
                        article.update(scraped)
                return article
        
        # Process articles concurrently
        tasks = [scrape_single(article) for article in articles]
        enhanced_articles = await asyncio.gather(*tasks)
        
        return enhanced_articles
    
    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()

content_service = ContentService()