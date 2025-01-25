import { Mistral } from '@mistralai/mistralai';

const apiKey = process.env.MISTRAL_API_KEY || 'your_api_key';

const client = new Mistral({ apiKey });

// On met la logique dans une fonction async
async function runChat() {
  const chatResponse = await client.chat.complete({
    model: 'mistral-tiny',
    messages: [{ role: 'user', content: 'What is the best French cheese?' }],
  });
  console.log('Chat:', chatResponse.choices[0].message.content);
}

// Exécution
runChat().catch(console.error);

