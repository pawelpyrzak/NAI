import logging
import openai
import json
from django.http import JsonResponse

openai.api_key = ""

logger = logging.getLogger(__name__)

def get_bot_response(request):
    if request.method == "POST":
        try:
            # Ekstrakcja JSON z żądania
            body = json.loads(request.body)
            user_message = body.get("message", "")

            if not user_message:
                return JsonResponse({"error": "Brak wiadomości w żądaniu."}, status=400)

            # # Wywołanie API OpenAI
            # response = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[
            #         {"role": "user", "content": user_message}
            #     ]
            # )
            #
            # bot_reply = response['choices'][0]['message']['content']

            bot_reply="<h1>hello</h1>"
            return JsonResponse({"response": bot_reply}, status=200)

        except json.JSONDecodeError:
            logger.exception("Nieprawidłowy JSON w żądaniu.")
            return JsonResponse({"error": "Nieprawidłowy format JSON."}, status=400)

        # except openai.error.OpenAIError as e:
        #     logger.exception("Błąd podczas wywoływania OpenAI API.")
        #     return JsonResponse({"error": "Błąd API OpenAI.", "details": str(e)}, status=500)

        except Exception as e:
            logger.exception("Nieoczekiwany błąd.")
            return JsonResponse({"error": "Wystąpił nieoczekiwany błąd.", "details": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Metoda GET jest niedozwolona."}, status=405)
