from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
import json
import time
import base64

# THESE ARE THE INPUTS I NEED
frontend_input = "Make me a dark and casual outfit for fall" 
frontend_image = "profile/person.png"

BASE_CLOSET_PATH = "/Users/senay/Gemini-App/backend"
MY_API_KEY = os.getenv("GEMINI_API_KEY")
MY_API_KEY = "AIzaSyC9MGtG_n_4oXfb0-iBWQbMahDzwrkBXiU"

client = genai.Client(api_key=MY_API_KEY)

INVENTORY_DATA = {
    # --- TOPS ---
    "Tops/hoodie1.jpg": {
        "clothing_type": "hoodie",
        "color": "Red",
        "material": "Wool Blend",
        
        "season_suitability": "Winter, Fall",
        "description": "Red, light weight, baggy, colorful."
    },
    "Tops/hoodie2.jpg": {
        "clothing_type": "hoodie",
        "color": "Brown",
        "material": "Polyester",
        "season_suitability": "Fall, Spring",
        "description": "Brown, medium weight, baggy, striped."
    },
    "Tops/jacket1.jpg": {
        "clothing_type": "jacket",
        "color": "Black",
        "material": "Suede",
        "season_suitability": "Winter, Fall",
        "description": "Black, sporty, trendy."
    },
    "Tops/sweater1.jpg": {
        "clothing_type": "sweater",
        "color": "Grey",
        "material": "Wool Blend",
        "season_suitability": "Winter, Fall",
        "description": "Grey, light weight, textured, professional."
    },
    "Tops/polo1.jpg": {
        "clothing_type": "polo shirt",
        "color": "Black",
        "material": "Wool Blend",
        "season_suitability": "Spring, Summer",
        "description": "Black, light weight, professional."
    },
    "Tops/polo2.jpg": {
        "clothing_type": "polo shirt",
        "color": "Green",
        "material": "Wool Blend",
        "season_suitability": "Spring, Summer",
        "description": "Green, striped, casual."
    },
    "Tops/polo3.jpg": {
        "clothing_type": "polo shirt",
        "color": "Blue",
        "material": "Wool Blend",
        "season_suitability": "Spring, Summer",
        "description": "Blue, plain, business casual."
    },
    # --- BOTTOMS ---
    "Bottoms/jeans1.jpg": {
        "clothing_type": "Jeans",
        "color": "Black",
        "material": "Denim",
        "season_suitability": "Winter, Fall, Spring, Summer",
        "description": "Tight fit, washed, casual."
    },
    "Bottoms/jeans2.jpg": {
        "clothing_type": "Jeans",
        "color": "Blue",
        "material": "Denim",
        "season_suitability": "Fall, Spring, Summer",
        "description": "trousers for cold days."
    },
    "Bottoms/jeans3.jpg": {
        "clothing_type": "Jeans",
        "color": "Black",
        "material": "Denim",
        "season_suitability": "Winter, Fall, Spring, Summer",
        "description": "Slim fit, professional."
    },
    "Bottoms/lightwashjeans.jpg": {
        "clothing_type": "Jeans",
        "color": "Light Wash Blue",
        "material": "Denim",
        "season_suitability": "Winter, Fall, Spring, Summer",
        "description": "Chill stacked fit fun"
    },
    "Bottoms/graysweats.jpg": {
        "clothing_type": "Sweatpants",
        "color": "Gray",
        "material": "Cotton",
        "season_suitability": "Winter, Fall, Spring, Summer",
        "description": "Lazy comfortable warm cozy"
    },
    "Bottoms/bluejeans.jpg": {
        "clothing_type": "Jeans",
        "color": "Blue",
        "material": "Denim",
        "season_suitability": "Winter, Fall, Spring, Summer",
        "description": "Most basic blue jeans very safe common"
    },
    "Bottoms/A46740001-front-gstk.jpeg": {
        "clothing_type": "Chinos",
        "color": "Khaki",
        "material": "Cotton",
        "season_suitability": "Winter, Fall, Spring, Summer",
        "description": "Light colored chinos very versatile"
    }
    
    
    
}

OUTFIT_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "best_top_path": types.Schema(
            type=types.Type.STRING,
            description="The EXACT file path (key) of the single best item suitable for a Top layer (like a shirt, sweater, or jacket) from the inventory."
        ),
        "best_bottom_path": types.Schema(
            type=types.Type.STRING,
            description="The EXACT file path (key) of the single best item suitable for a Bottom layer (like trousers, shorts, or a skirt) from the inventory."
        )
    },
    required=["best_top_path", "best_bottom_path"]
)

# --- API UTILITY (Same as before for robustness) ---

def call_api_with_retry(api_function, max_retries=5):
    """Handles transient API errors with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return api_function()
        except (genai.errors.APIError, json.JSONDecodeError) as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s...
                print(f"API Error: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts. Last error: {e}")
                raise

# --- MAIN LOGIC ---

def recommend_outfit(user_request: str):
    """
    Sends the user request and the inventory to Gemini for a structured outfit recommendation.
    """
    try:
        client = genai.Client(api_key=MY_API_KEY)
    except Exception as e:
        print(f"Error initializing Gemini client: {e}")
        print("Please ensure your GEMINI_API_KEY environment variable is set.")
        return

    # Prepare the inventory data for the LLM
    inventory_json_string = json.dumps(INVENTORY_DATA, indent=2)

    # Construct the full prompt for the AI
    system_instruction = (
        "You are an expert personal stylist. Your task is to recommend one Top item "
        "and one Bottom item from the provided INVENTORY. You MUST respond with a single "
        "JSON object that strictly adheres to the provided schema and contains ONLY the two file paths. "
        "The selected items MUST be compatible with the user's request (e.g., season, occasion) "
        "and be color-coordinated. Do not include any additional text or summaries."
    )

    user_prompt = (
        f"The user's request is: '{user_request}'\n\n"
        f"INVENTORY (Keys are file paths/IDs and values are metadata):\n"
        f"{inventory_json_string}\n\n"
        f"Please select the single best Top and single best Bottom to form a cohesive outfit and provide ONLY the structured output."
    )

    def api_call():
        """The actual Gemini API call logic."""
        # FIX: The system_instruction needs to be passed in the contents array for this client version.
        contents = [
        types.Content(role="user", parts=[
            types.Part.from_text(text=system_instruction),
            types.Part.from_text(text=user_prompt),
        ]),
]
        response = client.models.generate_content(
            model='gemini-2.5-flash', # gemini-2.5-flash
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=OUTFIT_SCHEMA,
            ),
        )
        json_string = response.text.strip()
        return json.loads(json_string)

    print("--- Sending Request to Personal AI Stylist ---")
    print(f"Request: '{user_request}'")
    
    try:
        recommendation = call_api_with_retry(api_call)
        print("Recommendation Received.")
        
        # Display ONLY the requested paths
        top_path = recommendation.get('best_top_path', 'N/A')
        bottom_path = recommendation.get('best_bottom_path', 'N/A')
        
        print("\n--- Recommendation (Paths Only) ---")
        print(f"Best Top Path:    {top_path}")
        print(f"Best Bottom Path: {bottom_path}")
        
        # <<< FIX: Now returning the recommendation data >>>
        return recommendation 
    except Exception as e:
        print(f"\nFailed to generate recommendation. Error: {e}")
        return None


def generate_outfit_image(user_prompt: str, person_image_path: str = None) -> dict:
    """
    Generate an outfit image based on user prompt and person image.
    Returns a dict with 'success', 'image_base64', and optionally 'error'.
    """
    try:
        # Use default person image path if not provided
        if person_image_path is None:
            person_image_path = os.path.join(BASE_CLOSET_PATH, frontend_image)
        
        # Step 1: Get outfit recommendation
        recommendation = recommend_outfit(user_prompt)
        
        if not recommendation:
            return {
                'success': False,
                'error': 'Failed to get outfit recommendation'
            }
        
        top_path_key = recommendation.get('best_top_path')
        bottom_path_key = recommendation.get('best_bottom_path')
        
        if not top_path_key or not bottom_path_key:
            return {
                'success': False,
                'error': 'Missing top or bottom path in recommendation'
            }
        
        # Step 2: Construct absolute paths and load images
        person_image_full_path = os.path.join(BASE_CLOSET_PATH, person_image_path) if not os.path.isabs(person_image_path) else person_image_path
        clothes_image1_path = os.path.join(BASE_CLOSET_PATH, top_path_key)
        clothes_image2_path = os.path.join(BASE_CLOSET_PATH, bottom_path_key)
        
        # Step 3: Load images
        try:
            person_image = Image.open(person_image_full_path)
            clothes_image1 = Image.open(clothes_image1_path)
            clothes_image2 = Image.open(clothes_image2_path)
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f'Image file not found: {e}'
            }
        
        # Step 4: Generate image with Gemini
        img_prompt = (
            "There is an image of a person and images of additional clothes. "
            "Generate an image of the person wearing the clothes provided, make sure both of "
            " the clothes provided are replaced from what the person was originally wearing on"
            " AND make sure the person is upright and centered"
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[img_prompt, person_image, clothes_image1, clothes_image2],
        )
        
        # Step 5: Extract generated image and convert to base64
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                generated_image = Image.open(BytesIO(part.inline_data.data))
                
                # Save to test3.png
                img_path = os.path.join(BASE_CLOSET_PATH, "test3.png")
                generated_image.save(img_path)
                print(f"Generated image saved as {img_path}")
                
                # Convert to base64
                img_buffer = BytesIO()
                generated_image.save(img_buffer, format='PNG')
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                
                return {
                    'success': True,
                    'image_base64': img_base64,
                    'format': 'PNG'
                }
        
        return {
            'success': False,
            'error': 'No image generated from Gemini API'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error generating outfit image: {str(e)}'
        }


# Keep the original script execution for backward compatibility
if __name__ == "__main__" or not hasattr(__import__('sys').modules[__name__], 'generate_outfit_image'):
    recommendation = recommend_outfit(frontend_input)

    if recommendation:
        top_path_key = recommendation.get('best_top_path')
        bottom_path_key = recommendation.get('best_bottom_path')
        if top_path_key and bottom_path_key:
            
            # 2. Construct absolute paths and load images dynamically
            
            person_image_path = os.path.join(BASE_CLOSET_PATH, frontend_image)
            print("the images", person_image_path)
            
            clothes_image1_path = os.path.join(BASE_CLOSET_PATH, top_path_key)
            clothes_image2_path = os.path.join(BASE_CLOSET_PATH, bottom_path_key)
        else:
            print("error2")
    else:
        print("error1")
    try:
        person_image = Image.open(person_image_path)
        clothes_image1 = Image.open(clothes_image1_path)
        clothes_image2 = Image.open(clothes_image2_path)

    except FileNotFoundError as e:
        print(f"Error: Image file not found. Please check your paths. {e}")
        exit()

    img_prompt = (
        "There is an image of a person and images of additional clothes. "
        "Generate an image of the person wearing the clothes provided, make sure both of "
        " the clothes provided are replaced from what the person was originally wearing on"
        " AND make sure the person is upright and centered"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[img_prompt, person_image, clothes_image1, clothes_image2], # <--- Key change here!
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text) 
        elif part.inline_data is not None:
            generated_image = Image.open(BytesIO(part.inline_data.data))
            img_path = "test3.png"        # <--- Key change here!
            generated_image.save(img_path)    
            print(f"Generated image saved as {img_path}")