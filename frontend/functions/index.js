// The Cloud Functions for Firebase SDK to create Cloud Functions and triggers.
const functions = require('firebase-functions');
// The Firebase Admin SDK to access Cloud Firestore.
const admin = require('firebase-admin');
admin.initializeApp();
const db = admin.firestore();

// Plaid Node.js client library
const { Configuration, PlaidApi, Products, CountryCode } = require('plaid');

// --- 1. Set up your Plaid Configuration ---
// These values will be securely retrieved from Firebase Functions Secrets
// We'll set these secrets in the terminal shortly.
const PLAID_CLIENT_ID = process.env.PLAID_CLIENT_ID;
const PLAID_SECRET = process.env.PLAID_SECRET;
const PLAID_ENV = 'sandbox'; // You can change this to 'development', 'production' as needed

const configuration = new Configuration({
  basePath: PlaidApi.environments[PLAID_ENV],
  baseOptions: {
    headers: {
      'PLAID-CLIENT-ID': PLAID_CLIENT_ID,
      'PLAID-SECRET': PLAID_SECRET,
      'Plaid-Version': '2020-09-14', // It's good practice to pin a Plaid API version
    },
  },
});

const client = new PlaidApi(configuration);

// --- 2. Cloud Function to Create a Link Token ---
exports.createLinkToken = functions.https.onCall(async (data, context) => {
  // Ensure the user is authenticated
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'The function must be called while authenticated.');
  }

  const clientUserId = context.auth.uid; // Get the Firebase Auth UID

  try {
    const createTokenResponse = await client.linkTokenCreate({
      user: {
        client_user_id: clientUserId,
      },
      client_name: 'Clarity Cash AF', // Your app name
      products: [Products.Transactions, Products.Auth], // What data you want to access
      country_codes: [CountryCode.Us], // E.g., United States
      language: 'en',
      webhook: 'https://webhook.your-app-domain.com/plaid-webhook', // Optional, for real-time updates
      // redirect_uri: 'https://your-app-domain.com/oauth-callback', // Required for some OAUTH flows
    });
    return { link_token: createTokenResponse.data.link_token };
  } catch (error) {
    console.error('Error creating link token:', error.response ? error.response.data : error);
    throw new functions.https.HttpsError('internal', 'Unable to create link token.', error.response ? error.response.data : error);
  }
});

// --- 3. Cloud Function to Exchange Public Token for Access Token ---
exports.exchangePublicToken = functions.https.onCall(async (data, context) => {
  // Ensure the user is authenticated
  if (!context.auth) {
    throw new functions.https.HttpsError('unauthenticated', 'The function must be called while authenticated.');
  }

  const { publicToken } = data; // publicToken sent from your frontend
  const uid = context.auth.uid;

  if (!publicToken) {
    throw new functions.https.HttpsError('invalid-argument', 'The function must be called with a publicToken.');
  }

  try {
    const exchangeResponse = await client.itemPublicTokenExchange({
      public_token: publicToken,
    });

    const accessToken = exchangeResponse.data.access_token;
    const itemId = exchangeResponse.data.item_id;

    // Store the access_token and item_id securely in Firestore under the user's document
    await db.collection('users').doc(uid).collection('plaid').doc(itemId).set({
      access_token: accessToken,
      created_at: admin.firestore.FieldValue.serverTimestamp(),
      // You might want to fetch and store more initial details here,
      // like institution name, accounts array, etc., using other Plaid API calls
      // (e.g., client.accountsGet({ access_token }))
    });

    return { success: true, item_id: itemId };

  } catch (error) {
    console.error('Error exchanging public token:', error.response ? error.response.data : error);
    throw new functions.https.HttpsError('internal', 'Unable to exchange public token.', error.response ? error.response.data : error);
  }
});
