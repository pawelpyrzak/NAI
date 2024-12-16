# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# import torch
# INTENT_DESCRIPTIONS = {
#     "todayTasks": ["tasks for today", "dzisiejsze zadania", "what needs to be done today"],
#     "upcomingTasks": ["upcoming tasks", "najbliższe zadania", "what's coming next", "tasks for the week",
#                       "zadania na tydzień", "weekly overview"],
#     "TodayMeetings": ["show today meetings", "dzisiejsze spotkania", "spotkania na dziś"],
#     "upcomingMeetings": ["upcoming meetings", "pokaż najbliższy spotkania", "najbliższe spotkania"],
#     "scheduleToday": ["show today schedule", "kalendarz", "schedule",
#                       "dzisiejszy kalendarz", "co w kalendarzu", "plan na dziś", "harmonogram dnia"]
# }
# # Załaduj model XLM-RoBERTa i tokenizer
# model_name = "xlm-roberta-base"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=len(INTENT_DESCRIPTIONS))
#
# # Funkcja klasyfikacji
# def classify_intent_with_xlm_roberta(user_message):
#     # Tokenizacja wiadomości
#     inputs = tokenizer(user_message, return_tensors="pt", padding=True, truncation=True, max_length=512)
#
#     # Uzyskiwanie wyników modelu
#     with torch.no_grad():
#         outputs = model(**inputs)
#
#     # Wyciąganie wyników
#     logits = outputs.logits
#     probabilities = torch.nn.functional.softmax(logits, dim=-1)
#     scores = probabilities.squeeze().tolist()
#
#     # Dopasowanie do intencji
#     intent_scores = zip(INTENT_DESCRIPTIONS.keys(), scores)
#     sorted_intents = sorted(intent_scores, key=lambda x: x[1], reverse=True)
#
#     # Zwracamy intencję z najwyższym wynikiem
#     return sorted_intents[0][0], sorted_intents[0][1]
#
# # Przykładowe INTENT_DESCRIPTIONS
#
#
# # Klasyfikacja przykładowej wiadomości
# user_message = "zadania na dziś"
# intent, score = classify_intent_with_xlm_roberta(user_message)
# print(f"Najlepsza intencja: {intent}, Zaufanie: {score:.4f}")
