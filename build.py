"""Generate the public school pages as standalone HTML documents."""
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import unquote

from school_copy import PAGES, EXTRA, BLOG

ROOT = 'https://www.tsggurukul.com'
DIST = Path('dist')
DATA = json.loads(Path('school-data.json').read_text(encoding='utf-8'))
ASSETS = set(p.name for p in (DIST / 'assets').iterdir())
ADDRESS = '444 Gothapatana, Malipada, Khandagiri, Bhubaneswar 751003, Odisha'
MAP = 'https://www.google.com/maps/search/?api=1&query=TSG+Gurukul+School+Bhubaneswar'
DIRS = {
 'About': ['about-us','profile','mission','chairman-message','mandatory-enclosure'],
 'Admissions': ['admission','instructions-for-admission','/application','fee-details','admission-criteria','rules-and-regulations','payment-policy'],
 'Academics': ['academics','course','academic-classroom','entrance-coaching','academic-calendar','exam','faculty','higher-studie'],
 'Campus Life': ['facilities','infrastructure','library','lab','it-club','smart-classrooms','campus-locations','medical-care','remedial-coaching','transportation','parental-visit','activities','sports','martial-arts','fine-arts-music','cultural-practice','social-responsibility'],
 'Boarding': ['hostel-and-cuisine','boarding-option','health-and-food','laundry','house-keeping','campus-rule-of-hostel'],
 'Gallery': ['/photo-gallery','/video-gallery'],
}
UTIL = ['/contact-us','/enquiry','/career','/blog','/faq','/certificate','help','privacy-policy','terms-and-conditions','site-map']
SUBGROUPS = {
 'infrastructure': ['library','lab','it-club','smart-classrooms'],
 'activities': ['sports','martial-arts','fine-arts-music','cultural-practice','social-responsibility'],
 'course': ['academic-classroom','entrance-coaching'],
}
ICONS = {
 'pin':'<path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
 'phone':'<path d="M22 16.8v3a2 2 0 0 1-2.2 2 18 18 0 0 1-7.8-2.8 18 18 0 0 1-5.5-5.5A18 18 0 0 1 3.7 5.7 2 2 0 0 1 5.7 3h3a2 2 0 0 1 2 1.7l.5 2.8a2 2 0 0 1-.6 2l-1.2 1.2a14 14 0 0 0 5.5 5.5l1.2-1.2a2 2 0 0 1 2-.6l2.8.5a2 2 0 0 1 1.1 1.9Z"/>',
 'mail':'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
 'chevron':'<path d="m7 10 5 5 5-5"/>',
 'book':'<path d="M12 7c-3-3-7-3-10-2v14c3-1 7-1 10 2 3-3 7-3 10-2V5c-3-1-7-1-10 2v14"/>',
 'leaf':'<path d="M20 4C8 3 4 8 5 14c1 7 13 7 15-10Z"/><path d="M3 21 15 9"/>',
 'home':'<path d="m3 11 9-7 9 7v9h-6v-6H9v6H3Z"/>',
 'form':'<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4V2m6 2V2M9 10h6m-6 4h6m-6 4h4"/>',
 'image':'<rect x="3" y="4" width="18" height="16" rx="3"/><circle cx="9" cy="9" r="1.5"/><path d="m4 18 6-5 4 3 3-4 4 5"/>',
 'play':'<path d="m9 6 10 6-10 6Z" fill="currentColor" stroke-linejoin="round"/>',
 'search':'<circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5 5"/>',
 'menu':'<path d="M4 6h16M4 12h16M4 18h16"/>',
 'close':'<path d="m6 6 12 12M18 6 6 18"/>',
 'left':'<path d="m14 6-6 6 6 6"/>',
 'right':'<path d="m10 6 6 6-6 6"/>',
}

def icon(name):
    return f'<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'

def path(key):
    key = key if key.startswith('/') else '/pages/' + key
    return key.rstrip('/') + '/'

def label(key):
    if key in PAGES:
        return PAGES[key][0]
    if key.startswith('/blog-details/'):
        return BLOG[int(key.rsplit('/', 1)[-1])][0]
    return EXTRA[key][0]

def a(key, title=None, css=''):
    return f'<a class="{css}" href="{path(key)}">{escape(title or label(key))}</a>'

def external(url, title, css=''):
    return f'<a class="{css}" href="{escape(url)}">{escape(title)}</a>'

def image(name, alt, eager=False, css=''):
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img class="{css}" src="/assets/{name}.webp" alt="{escape(alt)}" {loading} decoding="async">'

def cover(url, alt, css=''):
    filename = Path(unquote(url)).stem
    if '/photo_gallery/' in url:
        filename = 'gallery-' + ''.join(c for c in filename if c.isdigit())
    src = '/assets/' + filename + '.webp' if filename + '.webp' in ASSETS else url
    return f'<img class="{css}" src="{escape(src)}" alt="{escape(alt)}" loading="lazy" decoding="async">'

def section(title, content, eyebrow='', css=''):
    return f'<section class="wrap block {css}"><div class="section-heading" data-reveal>{eyebrow_html(eyebrow) if eyebrow else ""}<h2>{title}</h2></div>{content}</section>'

def eyebrow_html(text):
    return f'<p class="eyebrow"><span></span>{escape(text)}</p>'

def dropdown(group, items, current):
    active = current in items
    name = escape(group)
    return f'<details class="nav-group"><summary{" class=active" if active else ""}>{name}{icon("chevron")}</summary><div class="dropdown">{"".join(a(i) for i in items)}</div></details>'

def header(current):
    nav = ''.join(dropdown(group, items, current) for group, items in DIRS.items())
    return f'''<a class="skip" href="#main">Skip to content</a><div class="topbar"><div class="wrap topbar-inner"><span>{icon('pin')} Gothapatana, Bhubaneswar</span><div class="utility">
    <a href="tel:+919438782020">{icon('phone')} +91 94387 82020</a><a href="/career/">Careers</a><a href="/contact-us/">Contact</a></div></div></div>
    <header class="site-header"><div class="wrap header-inner"><a class="brand" href="/" aria-label="TSG Gurukul home"><img src="/assets/logo.webp" alt="" width="48" height="48"><span><strong>TSG Gurukul</strong><small>BHUBANESWAR</small></span></a>
    <button type="button" class="icon-button menu-toggle" aria-expanded="false" aria-controls="main-nav" aria-label="Open navigation">{icon('menu')}</button>
    <nav class="navigation" id="main-nav" aria-label="Main navigation">{nav}{a('/blog','Stories','nav-stories')}<a href="/contact-us/" class="mobile-contact">Contact us</a></nav>
    <div class="header-actions"><button class="icon-button" type="button" data-search aria-label="Search website">{icon('search')}</button>{a('/enquiry','Enquire','button primary nav-cta')}</div></div></header>'''

def footer():
    return f'''<footer class="footer"><div class="wrap footer-grid">
    <div><a class="brand" href="/"><img src="/assets/logo.webp" alt="" width="51" height="51"><span><strong>TSG Gurukul</strong><small>BHUBANESWAR</small></span></a><p>A unit of Nilachal Educational Trust</p><div class="social">{external('https://www.instagram.com/tsggurukul/','Instagram')}{external('https://www.facebook.com/tsggurukulbbsr/','Facebook')}{external('https://www.youtube.com/@tsggurukul1215','YouTube')}</div></div>
    <div><h2>Explore</h2>{a('about-us','About Us')}{a('admission','Admissions')}{a('academics')}{a('facilities','Campus Life')}{a('hostel-and-cuisine')}{a('/blog')}</div>
    <div><h2>Family resources</h2>{a('/application')}{a('fee-details')}{a('academic-calendar')}{a('/faq','FAQ')}{a('/certificate')}{a('mandatory-enclosure')}</div>
    <div><h2>Visit or get in touch</h2><p>{ADDRESS}</p>{external('tel:+919438782020','+91 94387 82020')}{external('mailto:info@netgurukul.in','info@netgurukul.in')}{external(MAP,'Get directions')}{a('/contact-us')}</div></div>
    <div class="wrap footer-bottom"><span>© TSG Gurukul</span><div>{a('privacy-policy')}{a('terms-and-conditions')}{a('help')}{a('site-map')}{a('/career')}</div></div></footer>'''

def dialog_markup():
    return f'''<dialog id="search-box" class="search-box"><div class="dialog-top"><h2>Find a page</h2><button type="button" class="icon-button" data-close aria-label="Close search">{icon('close')}</button></div><label class="sr-only" for="site-search">Search pages</label><input type="search" id="site-search" placeholder="Try “fees”, “library” or “admission”" autocomplete="off"><div class="search-results" aria-live="polite"></div></dialog>
    <dialog id="lightbox" class="lightbox" aria-label="Gallery photo"><button type="button" class="icon-button dialog-close" data-close aria-label="Close photo">{icon('close')}</button><div class="lightbox-frame"><button type="button" class="icon-button" data-photo-prev aria-label="Previous photo">{icon('left')}</button><img alt=""><button type="button" class="icon-button" data-photo-next aria-label="Next photo">{icon('right')}</button></div><p class="lightbox-caption"></p></dialog>'''

def page(title, description, markup, route, home=False):
    favicon = '/assets/logo.webp'
    output = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <meta name="theme-color" content="#28223c"><meta name="description" content="{escape(description)}"><title>{escape(title)}{" | TSG Gurukul" if not home else ""}</title>
    <link rel="icon" href="{favicon}"><link rel="stylesheet" href="/assets/site.css"><script src="/assets/site.js" defer></script></head>
    <body>{header(route)}<main id="main" tabindex="-1">{markup}</main>{footer()}{dialog_markup()}</body></html>'''
    dest = DIST / path(route).strip('/') / 'index.html'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(output, encoding='utf-8')

def quick():
    actions = [('form','admission','Admissions','How to apply'),('book','academics','Academics','Programmes and courses'),('home','hostel-and-cuisine','Boarding','Life in the hostels'),('pin','/contact-us','Visit the campus','Directions and contacts')]
    return '<div class="quick-panel"><div class="wrap quick-grid">' + ''.join(
        f'<a href="{path(key)}"><span class="quick-icon">{icon(pic)}</span><span><strong>{title}</strong><small>{detail}</small></span></a>'
        for pic,key,title,detail in actions
    ) + '</div></div>'

def photo_url(name):
    return '/assets/' + name + '.webp'

def feature(key, title, pic, copy, alt):
    return f'''<a class="feature-card" href="{path(key)}" data-reveal>{image(pic,alt)}<div><h3>{title}</h3><p>{copy}</p></div></a>'''

def story_cards(limit=4):
    cards = []
    for n,(name,category,asset,_) in list(BLOG.items())[:limit]:
        cards.append(f'''<article class="story-card" data-reveal><a href="/blog-details/{n}/">{image(asset,'')}<div><span class="kicker">{escape(category)}</span><h3>{escape(name)}</h3><p><time datetime="2025-03-18">18 March 2025</time></p></div></a></article>''')
    return '<div class="card-grid stories">' + ''.join(cards) + '</div>'

def photo_item(src, label_text, group, markup):
    return f'<a href="{escape(src)}" class="photo-tile" data-photo data-group="{escape(group)}" data-caption="{escape(label_text)}">{markup}<span class="photo-expand">{icon("image")}</span></a>'

def homepage():
    founder = 'campus-locations' if 'campus-locations.webp' in ASSETS else 'blog-2'
    academic = 'academic-classroom' if 'academic-classroom.webp' in ASSETS else 'banner'
    hostel = 'boarding-option' if 'boarding-option.webp' in ASSETS else 'blog-2'
    sport = 'activities' if 'activities.webp' in ASSETS else 'banner_4'
    hero = f'''<section class="hero"><div class="hero-media">{image('banner','A TSG Gurukul student works with laboratory equipment',True)}</div><div class="hero-shade"></div>
    <div class="wrap hero-inner">{eyebrow_html('CBSE SCHOOL  ·  BHUBANESWAR, ODISHA')}
    <h1>Rooted in values.<br><em>Ready for tomorrow.</em></h1><p>Day and residential schooling that brings Gurukul values into a modern education.</p>
    <div class="actions">{a('admission','Explore Admissions','button primary')}{a('about-us','Discover Our School','button outline')}</div></div></section>{quick()}'''
    intro = f'''<section class="wrap block intro"><div class="intro-photo" data-reveal>{image(founder,'Students at TSG Gurukul')}<span>TSG Gurukul · Bhubaneswar</span></div>
    <div class="intro-copy" data-reveal>{eyebrow_html('THE SCHOOL')}<h2>Where tradition<br>meets <em>possibility.</em></h2>
    <p>Founded in 2005, TSG Gurukul pairs classroom learning with time for sport, the arts and shared responsibilities. Students are encouraged to ask questions, think independently and make the most of life on campus.</p>
    <div class="school-facts"><p><strong>2005</strong><span>Year founded</span></p><p><strong>CBSE</strong><span>Senior secondary affiliation</span></p></div>{a('about-us','About TSG Gurukul','button dark')}</div></section>'''
    features = '<div class="card-grid">' + ''.join([
        feature('academics','Academics',academic,'Explore the curriculum, subject choices and classroom experience.',''),
        feature('activities','Beyond the classroom',sport,'Get to know the sports, arts and cultural activities students can try.',''),
        feature('hostel-and-cuisine','Residential life',hostel,'See how boarding, meals and student support work on campus.',''),
    ]) + '</div>'
    achievers = []
    for number in range(16,0,-1):
        asset = f'achiever_{number}'
        src = photo_url(asset) if asset + '.webp' in ASSETS else f'{ROOT}/frontend/images/achivers/{asset}.jpg'
        markup = f'<img src="{escape(src)}" alt="TSG Gurukul student achievement announcement" loading="lazy" decoding="async">'
        achievers.append(photo_item(src,'TSG Gurukul student achievement announcement','achievements',markup))
    achievements = '<div class="achievement-track" aria-label="Achievement posters">' + ''.join(achievers) + '</div><div class="track-controls"><button type="button" class="icon-button" data-track="-1" aria-label="Scroll achievements back">' + icon('left') + '</button><button type="button" class="icon-button" data-track="1" aria-label="Scroll achievements forward">' + icon('right') + '</button></div>'
    video = f'''<div class="film-feature" data-reveal>{image('banner_4','A school gathering at TSG Gurukul')}<div>{eyebrow_html('CAMPUS ON FILM')}<h2>A closer look at TSG Gurukul.</h2><p>Watch films made by the school.</p>{a('/video-gallery','Explore Videos','button primary')}</div></div>'''
    map_block = f'''<div class="campus-contact"><div><h3>Gothapatana campus</h3><p>{ADDRESS}</p>{external(MAP,'Get Directions','button dark')}{a('/contact-us','Contact the School','button line')}</div><div><h3>Parents and visitors</h3><p>Find campus contact details or read reviews on Google Maps.</p>{external(MAP,'View on Google Maps','text-link')}</div></div>'''
    return hero + intro + section('Explore life at TSG Gurukul',features) + '<div class="tinted">' + section('Our Achievers',achievements) + '</div>' + '<section class="wrap block">' + video + '</section>' + section('Stories from our school',story_cards(4)+f'<div class="more">{a("/blog","View All Stories","button line")}</div>') + admission_cta() + section('Visit the campus',map_block)

def admission_cta():
    return f'''<section class="admission-cta"><div class="wrap cta-inner" data-reveal><div>{eyebrow_html('ADMISSIONS')}<h2>Plan your next step.</h2><p>Explore application requirements or speak with the admissions team.</p></div><div class="actions">{a('/application','Student Registration','button primary')}{a('/enquiry','Ask a Question','button outline')}</div></div></section>'''

def group_for(key):
    return next((group for group, routes in DIRS.items() if key in routes), None)

def intro_page(key,title,description,photo=None):
    group = group_for(key)
    label_group = f'<span>{group}</span> <span aria-hidden="true">/</span>' if group and group.lower()!=title.lower() else ''
    media = image(photo,'',True,'page-photo') if photo else ''
    return f'''<section class="page-mast {"with-photo" if photo else ""}"><div class="wrap page-inner"><div><div class="crumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span>{label_group}<span>{escape(title)}</span></div>
    <h1>{escape(title)}</h1><p>{escape(description)}</p></div>{media}</div></section>'''

def content_sections(blocks):
    return ''.join(f'<section class="article-part"><h2>{escape(title)}</h2><p>{escape(copy)}</p></section>' for title,copy in blocks)

def links_list(keys, current=None):
    return ''.join(f'<a href="{path(key)}"{" aria-current=page" if key==current else ""}>{escape(label(key))}</a>' for key in keys)

def subnav(key):
    group = group_for(key)
    if not group:
        return ''
    parent = next((k for k,v in SUBGROUPS.items() if key in v),None)
    if parent:
        siblings = [DIRS[group][0],parent,*SUBGROUPS[parent]]
    elif key in SUBGROUPS:
        siblings = [DIRS[group][0],key,*SUBGROUPS[key]]
    elif group == 'Campus Life':
        siblings = [k for k in DIRS[group] if not any(k in v for v in SUBGROUPS.values())]
    else:
        siblings = DIRS[group]
    return f'<aside class="side-nav" aria-label="In this section"><h2>{group}</h2>{links_list(siblings,key)}</aside>'

def article(key, inner):
    nav = subnav(key)
    return f'<div class="wrap block article-layout {"has-aside" if nav else ""}"><div class="article-content">{inner}</div>{nav}</div>'

def table(headers, rows):
    th = ''.join(f'<th scope="col">{escape(str(t))}</th>' for t in headers)
    body = ''.join('<tr>'+''.join(f'<td>{escape(str(c))}</td>' for c in row)+'</tr>' for row in rows)
    return f'<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable table"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'

def details(title, inner, css=''):
    return f'<details class="accordion {css}"><summary>{escape(title)}{icon("chevron")}</summary><div>{inner}</div></details>'

def doclink(url,title):
    return external(url,title,'button line')

def format_rate(value):
    return '—' if value.strip()=='-' else re.sub(r'\.00/-?$', '', value)

def fee_info():
    content = ''
    for grade, campuses in DATA['fees'].items():
        cards = []
        for campus, upfront, rates in campuses:
            if len(upfront)!=4 or len(rates)!=3:
                continue
            terms = list(zip(['Registration','Admission','Readmission','Caution deposit'], [
                f'{format_rate(value)} ({kind.lower()})' if value not in ('-','—') else '—' for value,kind in upfront
            ]))
            terms += list(zip(['Monthly','Quarterly','Yearly'],[format_rate(v) for v in rates]))
            definitions = ''.join(f'<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>' for k,v in terms)
            cards.append(f'<section class="fee-campus"><h3>{escape(campus.replace("-"," · "))}</h3><dl>{definitions}</dl></section>')
        content += details(grade,'<div class="fee-grid">'+''.join(cards)+'</div>','fee-grade')
    instructions = [
        ('Due dates and discounts','The school lists the 10th of each month as the payment deadline and a ₹300 daily late fee. Its published schedule offers a 5% discount on full-year payment. The fee schedule lists eligible modes, additional charges, and exceptions for holidays.'),
        ('Payment and withdrawals','The school lists payment through its app or portal, by cheque or demand draft, or at the school counter. Its schedule lists a ₹1,250 transfer certificate fee. Check the original schedule for the full non-payment and withdrawal terms.')
    ]
    return '<p class="note">Select a grade to view the published fees for each campus. Confirm amounts with admissions before making a payment.</p>' + content + content_sections(instructions) + external(ROOT+'/pages/fee-details','View the official fee schedule','text-link')

def extra_page_content(key):
    if key=='instructions-for-admission':
        years=['Nursery','LKG','UKG'] + [f'Standard {i}' for i in range(1,13)]
        age=table(['Entry grade','Minimum age on 1 September'],[(grade,f'{i+3} years') for i,grade in enumerate(years)])
        return '<h2>Age on entry</h2>'+age+'<div class="actions documents">'+a('/application','Student Registration','button dark')+doclink('https://tsggurukul.com/pdf/Prospectus-2026-27.pdf','Prospectus 2026–27 (PDF)')+doclink('https://tsggurukul.com/pdf/TSG_ADMISSION%20FINAL%20POSTER.pdf','Admissions Poster (PDF)')+'</div>'
    if key=='academic-calendar':
        return doclink('https://tsggurukul.com/frontend/documents/Annual%20Calendar%202025_26.pdf','Annual Calendar 2025–26 (PDF)')
    if key=='mandatory-enclosure':
        return '<div class="actions documents">'+a('/certificate','View Certificates','button dark')+external(ROOT+'/pages/mandatory-enclosure','Full official disclosure','button line')+'</div>'+details('Published teaching staff',table(['Name','Designation','Qualification','Professional qualification'],DATA['staff']))
    if key=='campus-locations':
        return external(MAP,'Get Directions','button dark') + a('/contact-us','Contact Us','button line')
    if key=='faculty':
        return a('mandatory-enclosure','Teaching Staff Directory','button line')
    if key in ('boarding-option','campus-rule-of-hostel','rules-and-regulations','payment-policy','admission-criteria','chairman-message'):
        return external(ROOT+'/pages/'+key,'Read the original school page','text-link')
    if key in ('privacy-policy','terms-and-conditions','help'):
        return a('/contact-us','Contact the School','button dark') + a('/faq','Open the FAQ','button line')
    return ''

def category_cards(key):
    chosen = {
        'admission':['instructions-for-admission','/application','fee-details','admission-criteria','rules-and-regulations','payment-policy'],
        'about-us':['profile','mission','chairman-message','mandatory-enclosure'],
        'academics':['course','academic-calendar','exam','faculty','higher-studie'],
        'facilities':['infrastructure','campus-locations','medical-care','remedial-coaching','transportation','parental-visit','activities'],
        'hostel-and-cuisine':['boarding-option','health-and-food','laundry','house-keeping','campus-rule-of-hostel'],
        **SUBGROUPS,
    }.get(key,[])
    if not chosen:
        return ''
    cards = ''.join(f'<a href="{path(option)}" class="resource-card"><h3>{escape(label(option))}</h3><p>{escape((PAGES.get(option) or EXTRA[option])[1])}</p></a>' for option in chosen)
    return '<div class="resource-grid">' + cards + '</div>'

def sitemap():
    groups = {'Home and school resources':['/',*UTIL], **DIRS, 'Stories':[f'/blog-details/{n}' for n in BLOG]}
    cards = ''.join(f'<section><h2>{title}</h2>' + ('<a href="/">Home</a>'+links_list(keys[1:]) if title.startswith('Home') else links_list(keys)) + '</section>' for title,keys in groups.items())
    return '<div class="wrap block sitemap">'+cards+'</div>'

def photo_gallery():
    filters = '<button type="button" aria-pressed="true" data-filter="all">All photos</button>' + ''.join(f'<button type="button" data-filter="{escape(c)}" aria-pressed="false">{escape(c)}</button>' for c in DATA['gallery'])
    body = ''
    for category, urls in DATA['gallery'].items():
        photos = []
        for n,url in enumerate(urls,1):
            asset = 'gallery-' + ''.join(c for c in Path(unquote(url)).stem if c.isdigit())
            src = photo_url(asset) if asset+'.webp' in ASSETS else url
            caption = f'{category}, photo {n}'
            photos.append(photo_item(src,caption,category,cover(url,caption)))
        body += f'<section class="gallery-section" data-category="{escape(category)}"><h2>{escape(category)}</h2><div class="photo-grid">{"".join(photos)}</div></section>'
    return f'<div class="wrap block"><div class="gallery-switch">{a("/photo-gallery","Photos","button dark")}{a("/video-gallery","Videos","button line")}</div><div class="filters" role="group" aria-label="Filter photos">{filters}</div>{body}</div>'

def video_gallery():
    videos = [('Campus Film',ROOT+'/frontend/videos/TSG_Recent_Video.mp4'),('TSG Gurukul School Film',ROOT+'/public/images/video_gallery/TSG_Ads_Video_2025.mp4')]
    videos += [(f'From the School Video Gallery {i}',url) for i,url in enumerate(DATA['videos'],1)]
    poster = photo_url('video-poster' if 'video-poster.webp' in ASSETS else 'banner')
    entries = ''.join(f'<article class="video-card"><video controls playsinline preload="none" poster="{poster}" aria-label="{escape(title)}" src="{escape(url)}"></video><div><h2>{escape(title)}</h2>{external(url,"Open video file","text-link")}</div></article>' for title,url in videos)
    return f'<div class="wrap block"><div class="gallery-switch">{a("/photo-gallery","Photos","button line")}{a("/video-gallery","Videos","button dark")}</div><div class="card-grid video-grid">{entries}</div></div>'

def contacts():
    teams = [('Admissions','admissions'),('Careers','career'),('General enquiries','info'),('Feedback','feedbacks'),('Grievances','grievances')]
    rows = ''.join(f'<div><h3>{title}</h3>{external(f"mailto:{address}@netgurukul.in",f"{address}@netgurukul.in")}</div>' for title,address in teams)
    numbers = ['9438782020','7326014177','9777033020','8249316216','9040090653']
    phones = ''.join(external('tel:+91'+n,'+91 '+n[:5]+' '+n[5:]) for n in numbers)
    return f'''<div class="wrap block contact-layout"><section class="contact-card"><h2>School contacts</h2><div class="team-list">{rows}</div></section><section class="contact-card"><h2>Call admissions</h2><div class="phone-list">{phones}</div><h2>Visit the campus</h2><p>{ADDRESS}</p>{external(MAP,'Get Directions','button dark')}</section></div>'''

def faq():
    answers = [
        ('What are the admission requirements?','Requirements vary by grade. The school usually requires an application, proof of age, academic records and an assessment where applicable.','instructions-for-admission'),
        ('How do I apply?','You can start the school’s application online or contact the admissions office for help.','/application'),
        ('How much are the fees, and is financial aid available?','Tuition varies by grade and campus. Ask admissions about available scholarship or financial-aid options.','fee-details'),
        ('Does the school provide transport?','The school runs buses on routes in and around Bhubaneswar. Ask the school to confirm the route, fees and stops closest to you.','transportation'),
        ('What extracurricular activities are available?','The school lists sports, dance, music and other activities such as drama, robotics and debate.','activities'),
        ('How does the school support student safety?','The school’s FAQ lists CCTV, entry controls, security staff, emergency drills and campus medical facilities.','rules-and-regulations'),
    ]
    return ''.join(details(q,f'<p>{escape(reply)}</p>'+a(key,css='text-link')) for q,reply,key in answers)

def careers():
    listing = ''.join(details(title,
        f'<p>{escape(count)} listed {"vacancy" if count=="1" else "vacancies"}{(" · "+escape(experience)) if experience else ""}</p>'
        +external(ROOT+'/career','View official posting and apply','text-link'))
        for title,count,experience in DATA['jobs'])
    return '<p class="note">These roles appeared on the school’s recruitment page. Check the official listing for current availability, qualifications and application deadlines.</p>'+listing+'<div class="actions documents">'+external(ROOT+'/career','Open Official Careers Page','button dark')+external('mailto:career@netgurukul.in','Email Recruitment','button line')+'</div>'

def simple_extra(key):
    if key=='/application':
        return content_sections([
            ('What the application asks for','The school’s application collects student details, family details, information about the proposed grade and boarding arrangement, and supporting documents.'),
            ('Before you begin','Read the admissions instructions and prepare the school records, identification and photographs requested for your year group.')
        ])+f'<div class="actions">{external(ROOT+"/application","Continue to School Application","button dark")}{a("instructions-for-admission",css="button line")}</div>'
    if key=='/enquiry':
        return content_sections([('Send an enquiry','Use the school’s online enquiry form or contact admissions directly to ask about grades, boarding and campus visits.')])+f'<div class="actions">{external(ROOT+"/enquiry","Open School Enquiry Form","button dark")}{external("tel:+919438782020","Call Admissions","button line")}</div><p class="note">Email {external("mailto:admissions@netgurukul.in","admissions@netgurukul.in","text-link")}</p>'
    if key=='/career':
        return careers()
    if key=='/faq':
        return faq()
    if key=='/certificate':
        return '<div class="resource-grid document-grid">'+doclink(ROOT+'/storage/certificate/68298_UpdateAffiliationLetter.pdf','Affiliation and Upgradation Letter (PDF)')+doclink(ROOT+'/storage/certificate/23132_TrustDeed.pdf','Trust Registration Deed (PDF)')+'</div>'+a('mandatory-enclosure',css='text-link')
    return ''

def generate():
    page('TSG Gurukul | School in Bhubaneswar','Day and residential schooling in Gothapatana, Bhubaneswar. Explore admissions, academics, campus life and boarding at TSG Gurukul.',homepage(),'/',True)
    for slug,(title,description,blocks) in PAGES.items():
        key = slug
        photo = slug if slug+'.webp' in ASSETS and slug not in ('fee-details','instructions-for-admission','rules-and-regulations','about-us') else None
        if slug == 'about-us' and 'infrastructure.webp' in ASSETS:
            photo = 'infrastructure'
        if key=='site-map':
            body = sitemap()
        elif key=='fee-details':
            body = article(key, fee_info())
        else:
            resources = category_cards(key)
            body = article(key,content_sections(blocks)+extra_page_content(key)+resources)
        page(title,description,intro_page(key,title,description,photo)+body,key)
    for key,(title,description) in EXTRA.items():
        custom = {'/contact-us':contacts,'/blog':lambda:'<div class="wrap block">'+story_cards()+'</div>','/photo-gallery':photo_gallery,'/video-gallery':video_gallery}
        body = custom[key]() if key in custom else article(key,simple_extra(key))
        page(title,description,intro_page(key,title,description)+body,key)
    for number,(title,category,asset,blocks) in BLOG.items():
        key=f'/blog-details/{number}'
        body = f'<div class="wrap block story-detail"><p class="kicker"><time datetime="2025-03-18">18 MARCH 2025</time></p>{content_sections(blocks)}{external(ROOT+key,"Read the original article","button line")}{a("/blog","All School Stories","button line")}</div>'
        page(title,category,intro_page(key,title,category,asset)+body,key)
    search = [{'name':'Home','href':'/','description':'TSG Gurukul Bhubaneswar'}]
    search += [{'name':x[0],'href':path(k),'description':x[1]} for k,x in {**PAGES,**EXTRA}.items()]
    search += [{'name':x[0],'href':path(f'/blog-details/{n}'),'description':x[1]} for n,x in BLOG.items()]
    (DIST/'assets'/'search.json').write_text(json.dumps(search,ensure_ascii=False), encoding='utf-8')
    page('Page Not Found','Return to the home page or use the site map.',intro_page('/404','Page Not Found','Use the site map or return to the home page.')+'<div class="wrap block actions"><a class="button dark" href="/">Go Home</a>'+a('site-map',css='button line')+'</div>','/404')
    dest = DIST/'404.html'
    if dest.exists():
        dest.unlink()
    (DIST/'404/index.html').rename(dest)
    (DIST/'404').rmdir()
    print(f'Generated {len(search)} public routes')

if __name__=='__main__':
    generate()
