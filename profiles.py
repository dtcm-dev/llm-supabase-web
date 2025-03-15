profiles = {
        1: {
            "name": "Customer Service",
            "model_name": "gpt-4o-mini",
            "temperature": 0.5,
            "personality": "You are a friendly customer service representative for a tech company.",
            "system_prompt": "You are a customer service AI. {personality}"
        },
        2: {
            "name": "Technical Support",
            "model_name": "gpt-4o",
            "temperature": 0.8,
            "personality": "You are a technical support specialist with deep knowledge of our products.",
            "system_prompt": "You are a technical support AI. {personality}"
        }
}