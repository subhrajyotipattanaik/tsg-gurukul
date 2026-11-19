const menu = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.navigation');
const groups = [...navigation.querySelectorAll('details')];
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const mobileLayout = window.matchMedia('(max-width: 980px)');

function setMenu(isOpen) {
  menu.setAttribute('aria-expanded', String(isOpen));
  menu.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
  navigation.classList.toggle('open', isOpen);
  if (!isOpen) {
    groups.forEach(group => { group.open = false; });
  }
}

menu.addEventListener('click', () => {
  setMenu(menu.getAttribute('aria-expanded') !== 'true');
});
mobileLayout.addEventListener('change', () => setMenu(false));
groups.forEach(group => {
  group.addEventListener('toggle', () => {
    if (group.open) {
      groups.filter(other => other !== group).forEach(other => { other.open = false; });
    }
  });
});
document.addEventListener('click', event => {
  if (!navigation.contains(event.target) && !menu.contains(event.target)) {
    setMenu(false);
  }
});
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape' || document.querySelector('dialog[open]')) return;
  const openGroup = groups.find(group => group.open);
  if (openGroup) {
    openGroup.open = false;
    openGroup.querySelector('summary').focus();
  } else if (menu.getAttribute('aria-expanded') === 'true') {
    setMenu(false);
    menu.focus();
  }
});

if ('IntersectionObserver' in window && !reducedMotion.matches) {
  const observer = new IntersectionObserver(entries => {
    entries.filter(entry => entry.isIntersecting).forEach(entry => {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.09 });
  document.querySelectorAll('[data-reveal]').forEach(element => {
    element.classList.add('reveal-ready');
    observer.observe(element);
  });
}

const search = document.querySelector('#search-box');
const input = search.querySelector('input');
const results = search.querySelector('.search-results');
let indexRequest;

function renderResults(records) {
  const query = input.value.trim().toLowerCase();
  const words = query.split(/\s+/).filter(Boolean);
  const matching = records.filter(record => {
    const text = (record.name + ' ' + record.description).toLowerCase();
    return words.every(word => text.includes(word));
  });
  const ordered = query
    ? [...matching.filter(record => record.name.toLowerCase().includes(query)),
        ...matching.filter(record => !record.name.toLowerCase().includes(query))]
    : matching;
  results.replaceChildren();
  for (const record of ordered.slice(0, 8)) {
    const link = document.createElement('a');
    const name = document.createElement('strong');
    const detail = document.createElement('span');
    link.href = record.href;
    name.textContent = record.name;
    detail.textContent = record.description;
    link.append(name, detail);
    results.append(link);
  }
  if (!ordered.length) {
    const message = document.createElement('p');
    message.textContent = 'No pages match your search.';
    results.append(message);
  }
}

async function refreshResults() {
  if (!indexRequest) {
    indexRequest = fetch('/assets/search.json').then(response => {
      if (!response.ok) throw new Error('Search index unavailable');
      return response.json();
    });
  }
  try {
    renderResults(await indexRequest);
  } catch {
    indexRequest = undefined;
    const link = document.createElement('a');
    link.href = '/pages/site-map/';
    link.textContent = 'Search is unavailable. Browse the site map.';
    results.replaceChildren(link);
  }
}
document.querySelector('[data-search]').addEventListener('click', () => {
  search.showModal();
  input.focus();
  refreshResults();
});
input.addEventListener('input', refreshResults);

for (const filter of document.querySelectorAll('[data-filter]')) {
  filter.addEventListener('click', () => {
    document.querySelectorAll('[data-filter]').forEach(button => {
      button.setAttribute('aria-pressed', String(button === filter));
    });
    document.querySelectorAll('[data-category]').forEach(section => {
      section.hidden = filter.dataset.filter !== 'all'
        && section.dataset.category !== filter.dataset.filter;
    });
  });
}

const lightbox = document.querySelector('#lightbox');
const lightboxPhoto = lightbox.querySelector('img');
const caption = lightbox.querySelector('.lightbox-caption');
const allPhotos = [...document.querySelectorAll('[data-photo]')];
let activePhotos = [];
let photoIndex = 0;

function showPhoto(index) {
  photoIndex = (index + activePhotos.length) % activePhotos.length;
  const photo = activePhotos[photoIndex];
  lightboxPhoto.src = photo.href;
  lightboxPhoto.alt = photo.dataset.caption;
  caption.textContent = photo.dataset.caption;
}
for (const photo of allPhotos) {
  photo.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    activePhotos = allPhotos.filter(item => item.dataset.group === photo.dataset.group);
    showPhoto(activePhotos.indexOf(photo));
    lightbox.showModal();
  });
}
function turnPhoto(direction) {
  if (lightbox.open && activePhotos.length) showPhoto(photoIndex + direction);
}
lightbox.querySelector('[data-photo-prev]').addEventListener('click', () => turnPhoto(-1));
lightbox.querySelector('[data-photo-next]').addEventListener('click', () => turnPhoto(1));
lightbox.addEventListener('keydown', event => {
  if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
    event.preventDefault();
    turnPhoto(event.key === 'ArrowLeft' ? -1 : 1);
  }
});
for (const dialog of document.querySelectorAll('dialog')) {
  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right
      || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
}

const track = document.querySelector('.achievement-track');
for (const control of document.querySelectorAll('[data-track]')) {
  control.addEventListener('click', () => {
    track.scrollBy({
      left: track.clientWidth * Number(control.dataset.track),
      behavior: reducedMotion.matches ? 'instant' : 'smooth',
    });
  });
}
