class CorePromptTemplates:
    '''Prompt templates for core module.'''
    @staticmethod
    def classify_query_prompt(query: str):
        """Get the username prompt."""
        return f"""
        Classify the query among these classifications:

        1. manual_query - If the user if asking a question that can be related to something found in an owner's manual.
        2. general - If the user is asking a general car question such as basic car tips, maintenance, etc.
        3. unrelated - If the user is asking something unrelated to cars, their manuals, and maintaining them.

        Query: {query}
        """
        
    def manual_prompt(query: str, manual_text: str):
        """Prompt to read handle uploaded manuals."""
        return f"""
            You are a helpful assistant. Answer the question using ONLY the information from the car manual below.
            
            Manual:
            {manual_text}
            
            Question:
            {query}
            
            If the answer is not found in the manual, say: "I couldn't find an exact answer in the manual."
            """
