# 📋 Guide des Bonnes Pratiques JavaScript - test.js

## Structure et organisation

### ✅ Bonnes pratiques appliquées

#### 1. **Variables globales en haut**
```javascript
const API_BASE_URL = window.location.origin;
let preloader, header, mobileMenuBtn, navMenu, navLinks;
```
- Facile à identifier
- Accessible pour debug
- Initialisées à `null` ou valeur par défaut

#### 2. **Données séparées du code**
```javascript
const carouselImages = [
    { url: '...', title: '...', description: '...' }
];
```
- Facilite la maintenance
- Permet de charger depuis une API plus tard

#### 3. **Fonctions petites et spécialisées**
- `toggleMobileMenu()` : une responsabilité
- `handleNavLinkClick()` : un cas d'usage spécifique
- `animateCounter()` : une tâche simple

#### 4. **Nommage cohérent**
- `init*` : Fonctions d'initialisation
- `handle*` : Gestionnaires d'événements
- `setup*` : Configuration d'événements
- `animate*` : Animations

---

## Gestion des événements

### ✅ Patterns appliqués

#### 1. **Fonction réutilisable pour click + touch**
```javascript
function addEventListeners(element, handler, options = {}) {
    if (!element) return;
    element.addEventListener('click', handler, { passive: true });
    element.addEventListener('touchstart', (e) => {
        e.preventDefault();
        handler(e);
    }, { passive: false, ...options });
}
```
**Avantages** :
- DRY (Don't Repeat Yourself)
- Cohérence garantie
- Facile à maintenir

#### 2. **Fonction pour Enter key**
```javascript
function addEnterKeyListener(input, handler) {
    if (!input) return;
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handler(e);
        }
    });
}
```
**Avantages** :
- Réutilisable partout où c'est nécessaire
- Prévient les bugs de répétition

#### 3. **Null-checks systématiques**
```javascript
if (!element) return;
if (response && response.length > 0) { ... }
if (e.touches && e.touches.length > 0) { ... }
```

---

## Gestion des requêtes API

### ✅ Patterns de requête

#### 1. **Structure fetch uniforme**
```javascript
const response = await fetch(url, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify(data),
    credentials: 'same-origin'  // ✅ Important pour Django
});
```

#### 2. **Gestion d'erreurs en cascade**
```javascript
if (response.ok) {
    // Succès
} else if (response.status === 403) {
    // Erreur CSRF spécifique
} else if (response.status === 404) {
    // Endpoint non trouvé
} else {
    // Erreur générique
}
```

#### 3. **Try-catch avec finally**
```javascript
try {
    // Tentative de requête
} catch (error) {
    // Gestion de l'erreur
} finally {
    // Restauration de l'état UI
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
}
```

---

## Gestion des ressources

### ✅ Cleanup patterns

#### 1. **Nettoyage des intervalles**
```javascript
if (aboutCarouselInterval) {
    clearInterval(aboutCarouselInterval);
    aboutCarouselInterval = null;  // Important pour GC
}
```

#### 2. **Déconnexion des observateurs**
```javascript
if (intersectionObserver) {
    intersectionObserver.disconnect();
    intersectionObserver = null;
}
```

#### 3. **Appel au déchargement**
```javascript
window.addEventListener('beforeunload', cleanupResources);
```

---

## Validation

### ✅ Patterns de validation

#### 1. **Fonction centralisée**
```javascript
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}
```
**Avantages** :
- Une seule source de vérité
- Facile à tester
- Facile à mettre à jour

#### 2. **Validations avant requête**
```javascript
if (!name || !email || !message) {
    showToast('Veuillez remplir tous les champs', 'error');
    return;
}

if (!isValidEmail(email)) {
    showToast('Email invalide', 'error');
    return;
}
```

---

## Accessibilité

### ✅ Patterns ARIA

#### 1. **Labels explicites**
```javascript
button.setAttribute('aria-label', 'Fermer la modal');
button.setAttribute('aria-expanded', 'false');
button.setAttribute('aria-current', 'true');
```

#### 2. **Attributs de rôle**
```javascript
element.setAttribute('role', 'alert');
element.setAttribute('aria-live', 'assertive');
element.setAttribute('aria-controls', 'carouselTrack');
```

---

## Débogage

### ✅ Logging patterns

#### 1. **Logs avec context**
```javascript
console.log('🔗 Initialisation du formulaire de contact...');
console.log('📌 URL de base:', API_BASE_URL);
console.log('✅ Réponse JSON:', result);
console.error('❌ Erreur d\'envoi:', error);
```

#### 2. **Conditions et états**
```javascript
console.log('isMobile:', isMobile, 'window width:', window.innerWidth);
console.log('Token CSRF:', csrfToken ? 'Présent' : 'Manquant');
```

---

## Anti-patterns à éviter

### ❌ À NE PAS FAIRE

#### 1. **Ne pas oublier les null-checks**
```javascript
// ❌ Mauvais
element.addEventListener('click', handler);

// ✅ Bon
if (element) {
    element.addEventListener('click', handler);
}
```

#### 2. **Ne pas mélanger click et touch sans raison**
```javascript
// ❌ Mauvais - code redondant
button.addEventListener('click', handler);
button.addEventListener('touchstart', (e) => {
    e.preventDefault();
    handler(e);
}, { passive: false });

// ✅ Bon
addEventListeners(button, handler);
```

#### 3. **Ne pas oublier le cleanup**
```javascript
// ❌ Mauvais - fuite mémoire
setInterval(() => { ... }, 1000);

// ✅ Bon
let intervalId = setInterval(() => { ... }, 1000);
window.addEventListener('beforeunload', () => {
    clearInterval(intervalId);
});
```

#### 4. **Ne pas supposer que les touches existent**
```javascript
// ❌ Mauvais
const x = e.touches[0].clientX;

// ✅ Bon
const x = e.touches[0]?.clientX || 0;
```

#### 5. **Ne pas ignorer les erreurs API**
```javascript
// ❌ Mauvais
const data = await response.json();

// ✅ Bon
if (response.ok) {
    const data = await response.json();
} else {
    console.error('Erreur:', response.status);
}
```

---

## Performance

### ✅ Optimisations appliquées

#### 1. **Debounce pour scroll/resize**
```javascript
let scrollTimeout;
window.addEventListener('scroll', () => {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(handleWindowScroll, 50);
});
```

#### 2. **Lazy loading images**
```javascript
img.loading = 'lazy';
img.setAttribute('loading', 'lazy');
```

#### 3. **Event delegation (parcours du DOM)**
```javascript
document.querySelector('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', handleSmoothScroll);
});
```

#### 4. **IntersectionObserver pour animations**
```javascript
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateElement(entry.target);
        }
    });
});
```

---

## Tests recommandés

### 🧪 Tests à effectuer

- [ ] Swipe sur mobile (gauche/droite)
- [ ] Clic sur les indicateurs du carousel
- [ ] Soumission du formulaire de contact
- [ ] Soumission de la newsletter
- [ ] Ouverture/fermeture des modales
- [ ] Clavier (Escape pour fermer, Enter pour soumettre)
- [ ] Touch sur les boutons (mobile)
- [ ] Animations au scroll
- [ ] Changement de thème
- [ ] Menu mobile sur petit écran

---

## Ressources

### 📚 Documentation

- [MDN - Event listeners](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)
- [MDN - Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [MDN - IntersectionObserver](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)
- [MDN - Touch Events](https://developer.mozilla.org/en-US/docs/Web/API/Touch_events)
- [W3C - ARIA](https://www.w3.org/WAI/ARIA/apg/)

---

## Conclusion

Ce code suit les meilleures pratiques modernes de JavaScript :
- ✅ DRY (Don't Repeat Yourself)
- ✅ SOLID principles
- ✅ Accessibilité WCAG
- ✅ Performance optimisée
- ✅ Sécurité renforcée
- ✅ Maintenance facilitée
