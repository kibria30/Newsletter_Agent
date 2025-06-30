from typing import List, Dict, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import asyncio
import os
from datetime import datetime

from ..services.content_service import content_service
from ..services.vector_service import vector_service
from ..services.email_service import email_service

class NewsletterState(TypedDict):
    user_interests: List[str]
    user_email: str
    search_queries: List[str]
    raw_articles: List[Dict]
    processed_articles: List[Dict]
    newsletter_content: str
    email_status: str
    error_message: str

class NewsletterAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        self.workflow = self.create_workflow()
    
    def create_workflow(self):
        """Create the LangGraph workflow"""
        workflow = StateGraph(NewsletterState)
        
        # Add nodes
        workflow.add_node("generate_queries", self.generate_search_queries)
        workflow.add_node("collect_content", self.collect_content)
        workflow.add_node("process_content", self.process_content)
        workflow.add_node("compose_newsletter", self.compose_newsletter)
        workflow.add_node("send_email", self.send_newsletter_email)
        
        # Define edges
        workflow.set_entry_point("generate_queries")
        workflow.add_edge("generate_queries", "collect_content")
        workflow.add_edge("collect_content", "process_content")
        workflow.add_edge("process_content", "compose_newsletter")
        workflow.add_edge("compose_newsletter", "send_email")
        workflow.add_edge("send_email", END)
        
        return workflow.compile()
    
    async def generate_search_queries(self, state: NewsletterState) -> NewsletterState:
        """Generate optimized search queries based on user interests"""
        interests = state["user_interests"]
        print(f"Generating search queries for interests in query generation: {interests}")

        # Create search queries for each interest
        queries = []
        for interest in interests:
            base_queries = [
                f"{interest} latest news technology",
                f"{interest} breakthrough innovation 2025",
                f"{interest} industry trends updates"
            ]
            queries.extend(base_queries)
        
        # Use LLM to generate more sophisticated queries
        try:
            prompt = f"""
            Generate 3 specific and effective search queries for finding the latest(2025 in need to mention year) technology news 
            about these topics: {', '.join(interests)}
            
            Focus on:
            - Recent developments and breakthroughs
            - Industry news and trends
            - Product launches and innovations
            
            Return only the search queries, one per line.
            """
            
            response = await self.llm.ainvoke(prompt)
            llm_queries = response.content.strip().split('\n')
            print(f"LLM response on query building: {response}")
            queries.extend([q.strip() for q in llm_queries if q.strip()])
            print(f"Generated queries including all: {queries}")

        except Exception as e:
            print(f"Error generating LLM queries: {e}")
        
        state["search_queries"] = queries[:10]  # Limit to 10 queries
        print(f"Final search queries: {state['search_queries']}")
        return state
    
    async def collect_content(self, state: NewsletterState) -> NewsletterState:
        """Collect content using Tavily and web scraping"""
        print(f"Collecting content for queries: {state['search_queries']}")
        try:
            # Search using Tavily
            articles = await content_service.search_content_tavily(
                interests=state["user_interests"],
                max_results=20
            )
            
            # Enhance with scraping if needed
            articles = await content_service.enhance_articles_with_scraping(articles)
            
            state["raw_articles"] = articles
            
        except Exception as e:
            state["error_message"] = f"Content collection failed: {e}"
            state["raw_articles"] = []
        
        return state
    
    async def process_content(self, state: NewsletterState) -> NewsletterState:
        """Process and filter collected content"""
        raw_articles = state["raw_articles"]
        
        if not raw_articles:
            state["processed_articles"] = []
            return state
        
        try:
            # Add articles to vector store
            vector_service.add_articles(raw_articles)
            
            # Remove duplicates and low-quality content
            processed_articles = []
            seen_titles = set()
            
            for article in raw_articles:
                title = article.get('title', '').lower()
                content = article.get('content', '')
                
                # Skip if duplicate or low quality
                if (title in seen_titles or 
                    len(content) < 100 or 
                    not title):
                    continue
                
                seen_titles.add(title)
                processed_articles.append(article)
            
            # Sort by relevance and recency
            processed_articles = sorted(
                processed_articles,
                key=lambda x: (
                    x.get('published_at', datetime.min),
                    len(x.get('content', ''))
                ),
                reverse=True
            )
            
            # Limit to top 10 articles
            state["processed_articles"] = processed_articles[:10]
            
        except Exception as e:
            state["error_message"] = f"Content processing failed: {e}"
            state["processed_articles"] = []
        
        return state
    
    async def compose_newsletter(self, state: NewsletterState) -> NewsletterState:
        """Compose the newsletter content using LLM"""
        articles = state["processed_articles"]
        interests = state["user_interests"]
        
        if not articles:
            state["newsletter_content"] = "No relevant articles found for your interests."
            return state
        
        try:
            # Create article summaries using LLM
            article_summaries = []
            for article in articles:
                summary_prompt = f"""
                Summarize this article in 2-3 sentences, focusing on the key insights:
                
                Title: {article['title']}
                Content: {article['content'][:500]}...
                
                Make it engaging and highlight why it's relevant to someone interested in {article['category']}.
                """
                
                response = await self.llm.ainvoke(summary_prompt)
                article['ai_summary'] = response.content.strip()
                article_summaries.append(article)
            
            # Generate newsletter HTML
            html_content = email_service.create_newsletter_html(
                articles=article_summaries,
                user_interests=interests
            )
            
            state["newsletter_content"] = html_content
            
        except Exception as e:
            state["error_message"] = f"Newsletter composition failed: {e}"
            state["newsletter_content"] = "Failed to compose newsletter."
        
        return state
    
    async def send_newsletter_email(self, state: NewsletterState) -> NewsletterState:
        """Send the newsletter via email"""
        try:
            user_email = state["user_email"]
            content = state["newsletter_content"]
            interests_str = ", ".join(state["user_interests"])
            
            subject = f"🤖 Your AI Newsletter: {interests_str} - {datetime.now().strftime('%Y-%m-%d')}"
            
            success = email_service.send_newsletter(
                to_email=user_email,
                subject=subject,
                html_content=content
            )
            
            state["email_status"] = "sent" if success else "failed"
            
        except Exception as e:
            state["error_message"] = f"Email sending failed: {e}"
            state["email_status"] = "failed"
        
        return state
    
    async def run_newsletter_generation(self, user_email: str, user_interests: List[str]) -> Dict:
        """Run the complete newsletter generation workflow"""
        initial_state = NewsletterState(
            user_interests=user_interests,
            user_email=user_email,
            search_queries=[],
            raw_articles=[],
            processed_articles=[],
            newsletter_content="",
            email_status="pending",
            error_message=""
        )
        
        # Execute the workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        return {
            "status": final_state["email_status"],
            "articles_found": len(final_state["processed_articles"]),
            "newsletter_content": final_state["newsletter_content"],
            "error": final_state.get("error_message", "")
        }

# Global instance
newsletter_agent = NewsletterAgent()