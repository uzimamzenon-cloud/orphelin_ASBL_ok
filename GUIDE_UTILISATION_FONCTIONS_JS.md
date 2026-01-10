# 📚 Guide d'utilisation des nouvelles fonctions

## 🆕 Nouvelles fonctions disponibles

### 1. `addEventListeners(element, handler, options)`
Ajoute un événement pour click ET touch d'un coup.

#### Signature
```javascript
addEventListeners(element, handler, options = {})
```

#### Paramètres
- `element` (HTMLElement) : L'élément à modifier
- `handler` (Function) : La fonction à exécuter
- `options` (Object) : Options supplémentaires pour addEventListener

#### Exemples
```javascript
// Exemple 1 : Bouton simple
addEventListeners(myButton, () => {
    console.log('Cliqué !');
});

// Exemple 2 : Avec paramètres
const button = document.getElementById('closeBtn');
addEventListeners(button, closeDonationModal);

// Exemple 3 : Avec options
addEventListeners(element, handler, {
    once: false,
    capture: false
});
```

#### Avantages
✅ Pas besoin d'ajouter deux listeners  
✅ Cohérent partout dans l'app  
✅ Moins de code  
✅ Prévient les oublis  

---

### 2. `addEnterKeyListener(input, handler)`
Exécute une action quand on appuie sur Enter dans un champ.

#### Signature
```javascript
addEnterKeyListener(input, handler)
```

#### Paramètres
- `input` (HTMLElement) : Le champ input/textarea
- `handler` (Function) : La fonction à exécuter

#### Exemples
```javascript
// Exemple 1 : Soumettre un formulaire
const emailInput = document.getElementById('emailInput');
const submitBtn = document.getElementById('submitBtn');

addEnterKeyListener(emailInput, () => {
    submitBtn.click();
});

// Exemple 2 : Avec validation
const searchInput = document.querySelector('input[type="search"]');
addEnterKeyListener(searchInput, (e) => {
    const query = searchInput.value.trim();
    if (query.length > 0) {
        performSearch(query);
    }
});

// Exemple 3 : Newsletter
addEnterKeyListener(newsletterInput, handleNewsletterSubmit);
```

#### Utilisation dans le code
```javascript
// Dans setupEventListeners()
if (newsletterInput && newsletterBtn) {
    addEnterKeyListener(newsletterInput, () => newsletterBtn.click());
}
```

---

### 3. `isValidEmail(email)`
Valide une adresse email.

#### Signature
```javascript
isValidEmail(email) -> Boolean
```

#### Paramètres
- `email` (String) : L'email à valider

#### Exemples
```javascript
// Exemple 1 : Validation simple
if (isValidEmail(userEmail)) {
    console.log('Email valide');
} else {
    console.log('Email invalide');
}

// Exemple 2 : Dans un formulaire
const email = document.getElementById('email').value;
if (!isValidEmail(email)) {
    showToast('Email invalide', 'error');
    return;
}

// Exemple 3 : Avec trim
const email = userInput.value.trim();
if (isValidEmail(email)) {
    submitForm(email);
}

// Exemple 4 : Liste d'emails
const emails = ['user@example.com', 'invalid.email', 'admin@site.fr'];
const validEmails = emails.filter(isValidEmail);
console.log(validEmails);
// Sortie : ['user@example.com', 'admin@site.fr']
```

#### Formats validés
✅ `user@example.com`  
✅ `john.doe@company.co.uk`  
✅ `contact+tag@domain.org`  
❌ `invalid.email`  
❌ `@example.com`  
❌ `user@.com`  

---

### 4. `cleanupResources()`
Nettoie toutes les ressources de l'application.

#### Signature
```javascript
cleanupResources()
```

#### Paramètres
Aucun

#### Ce qu'elle nettoie
1. ✅ `aboutCarouselInterval` - Arrête le carrousel auto
2. ✅ `intersectionObserver` - Déconnecte l'observateur
3. ✅ `donationModal` - Ferme la modal de donation
4. ✅ `galleryModal` - Ferme la modal galerie

#### Quand elle est appelée
```javascript
// Automatiquement au déchargement de la page
window.addEventListener('beforeunload', cleanupResources);

// Ou manuellement si besoin
cleanupResources();
```

#### Exemple d'utilisation manuelle
```javascript
// Si vous lancez une nouvelle instance
cleanupResources();

// Puis réinitialisez
initCarousel();
initAboutCarousel();
```

---

### 5. `isValidEmail(email)`
Valide une adresse email (déjà décrite ci-dessus).

---

## 🔄 Refactorisation : Avant/Après

### Exemple 1 : Bouton avec événements tactiles

#### ❌ AVANT (Code redondant)
```javascript
// Code dupliqué partout
const button = document.getElementById('myBtn');

button.addEventListener('click', () => {
    myFunction();
});

button.addEventListener('touchstart', (e) => {
    e.preventDefault();
    myFunction();
}, { passive: false });
```

#### ✅ APRÈS (Nettoyé)
```javascript
const button = document.getElementById('myBtn');
addEventListeners(button, myFunction);
```

**Réduction** : 5 lignes → 1 ligne (-80%)

---

### Exemple 2 : Validation d'email

#### ❌ AVANT (Regex dupliquée)
```javascript
// Dans handleNewsletterSubmit
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) { ... }

// Dans initContactForm
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) { ... }

// Dans une autre fonction...
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
```

#### ✅ APRÈS (Fonction unique)
```javascript
// Définie une fois
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Utilisée partout
if (!isValidEmail(email)) { ... }
if (isValidEmail(userInput)) { ... }
```

**Avantage** : Une seule source de vérité

---

### Exemple 3 : Nettoyage des ressources

#### ❌ AVANT (Pas de nettoyage)
```javascript
let aboutCarouselInterval = setInterval(() => {
    // Code du carrousel
}, 4000);

// Jamais arrêté → Fuite mémoire
```

#### ✅ APRÈS (Nettoyage automatique)
```javascript
let aboutCarouselInterval = setInterval(() => {
    // Code du carrousel
}, 4000);

// Nettoyé automatiquement
window.addEventListener('beforeunload', cleanupResources);

function cleanupResources() {
    if (aboutCarouselInterval) {
        clearInterval(aboutCarouselInterval);
        aboutCarouselInterval = null;
    }
}
```

---

## 🎯 Cas d'usage courants

### Cas 1 : Créer un nouveau bouton avec événements

```javascript
// Supposons que vous ajoutez un nouveau bouton HTML
const newButton = document.querySelector('.new-button');

// Au lieu de faire :
newButton.addEventListener('click', handleClick);
newButton.addEventListener('touchstart', (e) => {
    e.preventDefault();
    handleClick(e);
}, { passive: false });

// Vous faites simplement :
addEventListeners(newButton, handleClick);
```

### Cas 2 : Valider un email dans un formulaire

```javascript
function handleFormSubmit(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value.trim();
    
    // Validation simple avec la fonction centralisée
    if (!isValidEmail(email)) {
        showToast('Email invalide', 'error');
        return;
    }
    
    // Continuer avec la soumission
    submitForm();
}
```

### Cas 3 : Créer un champ avec touche Enter

```javascript
function initCustomInput() {
    const input = document.getElementById('custom-input');
    const button = document.getElementById('custom-button');
    
    // Quand l'utilisateur appuie sur Enter, on clique le bouton
    addEnterKeyListener(input, () => button.click());
    
    // Quand on clique le bouton, on traite
    addEventListeners(button, processInput);
}
```

### Cas 4 : Nettoyer manuellement avant de recharger

```javascript
// Avant de naviguer vers une autre page
function navigateToNewPage(url) {
    cleanupResources();  // Nettoyer tous les listeners
    window.location.href = url;
}
```

---

## 🐛 Erreurs courantes à éviter

### ❌ Erreur 1 : Oublier le null-check
```javascript
// ❌ Mauvais - plante si element est null
addEventListeners(document.getElementById('missing'), handler);

// ✅ Bon - la fonction vérifie automatiquement
// La fonction addEventListeners fait : if (!element) return;
```

### ❌ Erreur 2 : Utiliser isValidEmail sans trim
```javascript
// ❌ Mauvais - possibles espaces
if (!isValidEmail(userInput.value)) { ... }

// ✅ Bon - supprimer les espaces
if (!isValidEmail(userInput.value.trim())) { ... }
```

### ❌ Erreur 3 : Oublier d'appeler cleanupResources
```javascript
// ❌ Mauvais
// ... crée des listeners et intervalles
// Ne pas nettoyer → fuite mémoire

// ✅ Bon
window.addEventListener('beforeunload', cleanupResources);
```

---

## 📊 Tableau de comparaison

| Tâche | Avant | Après | Gain |
|-------|-------|-------|------|
| Ajouter click + touch | 5 lignes | 1 ligne | -80% |
| Valider email | 3 endroits | 1 endroit | -66% |
| Nettoyer ressources | Manuel | Auto | 100% ✅ |
| Enter key | Répété | 1 fonction | -85% |

---

## 🚀 Prochaines optimisations

1. **Créer des utilitaires supplémentaires** :
   ```javascript
   function debounce(func, delay) { ... }
   function throttle(func, delay) { ... }
   function memoize(func) { ... }
   ```

2. **Utiliser des événements délégués** :
   ```javascript
   // Au lieu de listener sur chaque élément
   // Utiliser un seul listener sur le parent
   ```

3. **Ajouter des tests unitaires** :
   ```javascript
   // Avec Jest ou Mocha
   test('isValidEmail accepts valid emails', () => {
       expect(isValidEmail('test@example.com')).toBe(true);
   });
   ```

---

## 📞 Besoin d'aide ?

- ✅ Vérifier la console (F12)
- ✅ Consulter `CHANGELOG_JS.md` pour les détails
- ✅ Consulter `BONNES_PRATIQUES_JS.md` pour la structure
- ✅ Regarder les exemples dans `test.js`

**Dernière mise à jour** : 10 janvier 2026
