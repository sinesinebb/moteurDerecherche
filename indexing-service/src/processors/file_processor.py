from tika import parser
from lib.guesslang import Guess

class FileProcessor:
    def process_pdf(self, file_path):
        parsed = parser.from_file(file_path)
        content = parsed['content']
        
        # Détection du langage de code
        guess = Guess()
        language = guess.language_name(content) if content else 'Unknown'
        
        return {
            'content': content,
            'metadata': parsed['metadata'],
            'language': language
        }