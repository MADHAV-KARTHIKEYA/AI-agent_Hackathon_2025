import os
import logging
from typing import Dict, List
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIndexer:
    def __init__(self):
        self.documents = {}
        self.index = {}
    
    def index_documents(self) -> Dict[str, str]:
        """Index all documents in the docs folder"""
        try:
            if not os.path.exists(Config.DOCS_FOLDER):
                logger.warning(f"Documents folder '{Config.DOCS_FOLDER}' not found. Creating it...")
                os.makedirs(Config.DOCS_FOLDER)
                self._create_sample_docs()
            
            self.documents = {}
            
            for filename in os.listdir(Config.DOCS_FOLDER):
                if filename.endswith(('.txt', '.md')):
                    filepath = os.path.join(Config.DOCS_FOLDER, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as file:
                            content = file.read()
                            self.documents[filename] = content
                            logger.info(f"Indexed document: {filename}")
                    except Exception as e:
                        logger.error(f"Error reading file {filename}: {str(e)}")
            
            logger.info(f"Successfully indexed {len(self.documents)} documents")
            return self.documents
            
        except Exception as e:
            logger.error(f"Error during document indexing: {str(e)}")
            return {}
    
    def _create_sample_docs(self):
        """Create sample documents for demonstration"""
        sample_docs = {
            'refund_policy.txt': """REFUND POLICY

Our company offers a 30-day refund policy for all products and services.

Process to request a refund:
1. Contact customer support at support@company.com
2. Provide order number and reason for refund
3. Wait for approval (usually 2-3 business days)
4. Refund will be processed to original payment method

Exceptions:
- Digital products downloaded more than 7 days ago
- Custom services already delivered
- Products damaged by customer misuse

For questions, contact: finance@company.com
""",
            
            'design_assets.txt': """DESIGN ASSET REQUEST PROCESS

To request design assets, follow these steps:

1. Submit a request through our internal portal: design.company.com
2. Fill out the design brief with:
   - Project description
   - Target audience
   - Preferred style/brand guidelines
   - Deadline requirements
   - File format needed (PNG, SVG, PDF, etc.)

3. Design team will review within 24 hours
4. First draft delivered within 3-5 business days
5. Up to 2 rounds of revisions included

Contact: design-team@company.com
Slack channel: #design-requests

Brand guidelines available at: brand.company.com
""",
            
            'vacation_policy.txt': """VACATION AND TIME OFF POLICY

Annual Leave:
- New employees: 15 days per year
- 2+ years: 20 days per year  
- 5+ years: 25 days per year

How to request time off:
1. Submit request in HR system at least 2 weeks in advance
2. Get manager approval
3. Update team calendar
4. Set up out-of-office messages

Sick Leave:
- Unlimited sick days (within reason)
- Doctor's note required for 3+ consecutive days
- Notify manager as soon as possible

Contact HR at hr@company.com for questions.
""",
            
            'onboarding_process.txt': """NEW EMPLOYEE ONBOARDING

Week 1:
- IT setup (laptop, accounts, software access)
- HR orientation and paperwork
- Meet your team and manager
- Review company handbook
- Complete mandatory training modules

Week 2:
- Department-specific training
- Shadow experienced team members
- Set up development environment (if applicable)
- First project assignment

Resources:
- Employee handbook: handbook.company.com
- IT support: it-support@company.com
- HR questions: hr@company.com

30-60-90 Day Check-ins:
- 30 days: Initial feedback session
- 60 days: Goal setting and development plan
- 90 days: Performance review and role confirmation
"""
        }
        
        for filename, content in sample_docs.items():
            filepath = os.path.join(Config.DOCS_FOLDER, filename)
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            logger.info(f"Created sample document: {filename}")
    
    def search_documents(self, query: str) -> str:
        """Search for relevant content in indexed documents"""
        if not self.documents:
            self.index_documents()
        
        relevant_content = []
        query_lower = query.lower()
        
        for filename, content in self.documents.items():
            if any(keyword in content.lower() for keyword in query_lower.split()):
                relevant_content.append(f"From {filename}:\n{content}\n")
        
        if relevant_content:
            return "\n".join(relevant_content)
        else:
            return "No relevant documents found for your query."

# Global indexer instance
indexer = DocumentIndexer()
