from transformers import BartTokenizer, BartForConditionalGeneration


def generate_summary(text):
    # Tokenizer dla modelu BART
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

    # Tokenizacja i kodowanie tekstu wejściowego
    inputs = tokenizer(text, return_tensors='pt', max_length=1024, truncation=True)

    # Model BART
    model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

    # Generowanie podsumowania
    summary_ids = model.generate(inputs['input_ids'], num_beams=4, min_length=30, max_length=100, early_stopping=True)

    # Dekodowanie podsumowania
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary


# Przykładowy tekst do podsumowania
sample_text = """
Section 1.10.33 of "de Finibus Bonorum et Malorum", written by Cicero in 45 BC
"At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat."
"""

# Wygenerowanie podsumowania
generated_summary = generate_summary(sample_text)

print("Original Text:")
print(sample_text)
print("\nGenerated Summary:")
print(generated_summary)
