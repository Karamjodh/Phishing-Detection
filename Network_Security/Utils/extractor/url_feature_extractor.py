"""
Complete URL Feature Extractor for Phishing Detection
Extracts all 30 features used in phishing URL detection
"""

import re
import socket
import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from bs4 import BeautifulSoup
import whois
import ssl
import dns.resolver
from urllib.request import Request, urlopen
import warnings

warnings.filterwarnings('ignore')

class URLFeatureExtractor:
    """Extract all 30 features from a URL for phishing detection"""
    
    def __init__(self, url, timeout=5):
        self.url = url if url.startswith('http') else 'http://' + url
        self.timeout = timeout
        self.parsed = urlparse(self.url)
        self.domain = self.parsed.netloc
        self.path = self.parsed.path
        self.html_content = None
        self.soup = None
        
    def extract_all_features(self):
        """Extract all 30 features and return as dictionary"""
        features = {}
        
        # Address Bar Based Features (1-10)
        features['having_IP_Address'] = self.having_ip_address()
        features['URL_Length'] = self.url_length()
        features['Shortining_Service'] = self.shortening_service()
        features['having_At_Symbol'] = self.having_at_symbol()
        features['double_slash_redirecting'] = self.double_slash_redirecting()
        features['Prefix_Suffix'] = self.prefix_suffix()
        features['having_Sub_Domain'] = self.having_sub_domain()
        features['SSLfinal_State'] = self.ssl_final_state()
        features['Domain_registeration_length'] = self.domain_registration_length()
        features['Favicon'] = self.favicon()
        
        # Domain Based Features (11-14)
        features['port'] = self.port()
        features['HTTPS_token'] = self.https_token()
        
        # HTML/JavaScript Based Features (15-24)
        # These require fetching the webpage
        self.fetch_webpage_content()
        
        features['Request_URL'] = self.request_url()
        features['URL_of_Anchor'] = self.url_of_anchor()
        features['Links_in_tags'] = self.links_in_tags()
        features['SFH'] = self.sfh()
        features['Submitting_to_email'] = self.submitting_to_email()
        features['Abnormal_URL'] = self.abnormal_url()
        features['Redirect'] = self.redirect()
        features['on_mouseover'] = self.on_mouseover()
        features['RightClick'] = self.right_click()
        features['popUpWidnow'] = self.popup_window()
        features['Iframe'] = self.iframe()
        features['age_of_domain'] = self.age_of_domain()
        
        # Domain and Website Traffic Features (25-30)
        features['DNSRecord'] = self.dns_record()
        features['web_traffic'] = self.web_traffic()
        features['Page_Rank'] = self.page_rank()
        features['Google_Index'] = self.google_index()
        features['Links_pointing_to_page'] = self.links_pointing_to_page()
        features['Statistical_report'] = self.statistical_report()
        
        return features
    
    # ==================== ADDRESS BAR BASED FEATURES (1-10) ====================
    
    def having_ip_address(self):
        """Feature 1: Check if URL has IP address instead of domain"""
        try:
            # Check for IPv4
            pattern = r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])'
            if re.search(pattern, self.domain):
                return -1  # Phishing
            # Check for IPv6
            if re.search(r'[0-9a-fA-F]{1,4}:[0-9a-fA-F]{1,4}', self.domain):
                return -1  # Phishing
            return 1  # Legitimate
        except:
            return -1
    
    def url_length(self):
        """Feature 2: URL length"""
        length = len(self.url)
        if length < 54:
            return 1  # Legitimate
        elif 54 <= length <= 75:
            return 0  # Suspicious
        else:
            return -1  # Phishing
    
    def shortening_service(self):
        """Feature 3: Check for URL shortening service"""
        shortening_services = [
            'bit.ly', 'goo.gl', 'shorte.st', 'go2l.ink', 'x.co', 'ow.ly', 
            't.co', 'tinyurl', 'tr.im', 'is.gd', 'cli.gs', 'yfrog.com',
            'migre.me', 'ff.im', 'tiny.cc', 'url4.eu', 'twit.ac', 
            'su.pr', 'twurl.nl', 'snipurl.com', 'short.to', 'BudURL.com',
            'ping.fm', 'post.ly', 'Just.as', 'bkite.com', 'snipr.com',
            'fic.kr', 'loopt.us', 'doiop.com', 'short.ie', 'kl.am',
            'wp.me', 'rubyurl.com', 'om.ly', 'to.ly', 'bit.do',
            'lnkd.in', 'db.tt', 'qr.ae', 'adf.ly', 'bitly.com',
            'cur.lv', 'tinyurl.com', 'ity.im', 'q.gs', 'is.gd',
            'po.st', 'bc.vc', 'twitthis.com', 'u.to', 'j.mp',
            'buzurl.com', 'cutt.us', 'u.bb', 'yourls.org', 'prettylinkpro.com',
            'scrnch.me', 'filoops.info', 'vzturl.com', 'qr.net', '1url.com',
            'tweez.me', 'v.gd', 'link.zip.net'
        ]
        for service in shortening_services:
            if service in self.domain:
                return -1  # Phishing
        return 1  # Legitimate
    
    def having_at_symbol(self):
        """Feature 4: Check for @ symbol in URL"""
        return -1 if '@' in self.url else 1
    
    def double_slash_redirecting(self):
        """Feature 5: Check for // after protocol"""
        # Get position of first occurrence of //
        position = self.url.find('//')
        if position > 7:  # After http:// or https://
            return -1  # Phishing
        return 1  # Legitimate
    
    def prefix_suffix(self):
        """Feature 6: Check for - in domain"""
        return -1 if '-' in self.domain else 1
    
    def having_sub_domain(self):
        """Feature 7: Count number of subdomains"""
        dots = self.domain.count('.')
        if dots == 1:
            return 1  # Legitimate (domain.com)
        elif dots == 2:
            return 0  # Suspicious (sub.domain.com)
        else:
            return -1  # Phishing (sub.sub.domain.com)
    
    def ssl_final_state(self):
        """Feature 8: Check SSL certificate"""
        try:
            if self.parsed.scheme == 'https':
                # Try to verify SSL certificate
                ctx = ssl.create_default_context()
                with socket.create_connection((self.domain, 443), timeout=self.timeout) as sock:
                    with ctx.wrap_socket(sock, server_hostname=self.domain) as ssock:
                        cert = ssock.getpeercert()
                        # Check if certificate is valid
                        if cert:
                            return 1  # Legitimate
                return 0  # Suspicious
            else:
                return -1  # Phishing (no HTTPS)
        except:
            return -1  # Phishing
    
    def domain_registration_length(self):
        """Feature 9: Domain registration length"""
        try:
            domain_info = whois.whois(self.domain)
            if domain_info.expiration_date:
                if isinstance(domain_info.expiration_date, list):
                    expiration_date = domain_info.expiration_date[0]
                else:
                    expiration_date = domain_info.expiration_date
                
                if isinstance(domain_info.creation_date, list):
                    creation_date = domain_info.creation_date[0]
                else:
                    creation_date = domain_info.creation_date
                
                if expiration_date and creation_date:
                    registration_length = (expiration_date - creation_date).days
                    if registration_length >= 365:  # 1 year or more
                        return 1  # Legitimate
                    else:
                        return -1  # Phishing
            return -1
        except:
            return -1  # Phishing
    
    def favicon(self):
        """Feature 10: Check if favicon loaded from external domain"""
        try:
            if self.soup:
                for link in self.soup.find_all('link', rel='icon'):
                    favicon_url = link.get('href', '')
                    if favicon_url:
                        if favicon_url.startswith('http') and self.domain not in favicon_url:
                            return -1  # Phishing
                return 1  # Legitimate
            return 1
        except:
            return 1
    
    # ==================== DOMAIN BASED FEATURES (11-14) ====================
    
    def port(self):
        """Feature 11: Check if using non-standard port"""
        if self.parsed.port:
            if self.parsed.port not in [80, 443]:
                return -1  # Phishing
        return 1  # Legitimate
    
    def https_token(self):
        """Feature 12: Check for https token in domain part"""
        return -1 if 'https' in self.domain.lower() else 1
    
    # ==================== HTML/JAVASCRIPT BASED FEATURES (13-24) ====================
    
    def fetch_webpage_content(self):
        """Fetch webpage content for analysis"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.url, headers=headers, timeout=self.timeout, verify=False)
            self.html_content = response.text
            self.soup = BeautifulSoup(self.html_content, 'html.parser')
        except:
            self.html_content = ""
            self.soup = None
    
    def request_url(self):
        """Feature 13: % of external objects in page"""
        try:
            if self.soup:
                total_objects = 0
                external_objects = 0
                
                # Check images, videos, audio
                for tag in self.soup.find_all(['img', 'video', 'audio']):
                    src = tag.get('src', '')
                    if src:
                        total_objects += 1
                        if src.startswith('http') and self.domain not in src:
                            external_objects += 1
                
                if total_objects > 0:
                    percentage = (external_objects / total_objects) * 100
                    if percentage < 22:
                        return 1  # Legitimate
                    elif 22 <= percentage <= 61:
                        return 0  # Suspicious
                    else:
                        return -1  # Phishing
            return 1
        except:
            return 1
    
    def url_of_anchor(self):
        """Feature 14: % of anchor tags pointing to different domain"""
        try:
            if self.soup:
                anchors = self.soup.find_all('a', href=True)
                total_anchors = len(anchors)
                
                if total_anchors == 0:
                    return 1
                
                unsafe_anchors = 0
                for anchor in anchors:
                    href = anchor['href']
                    if href in ['#', '#content', '#skip', 'javascript:void(0)', 'javascript::void(0)']:
                        unsafe_anchors += 1
                    elif href.startswith('http') and self.domain not in href:
                        unsafe_anchors += 1
                
                percentage = (unsafe_anchors / total_anchors) * 100
                if percentage < 31:
                    return 1  # Legitimate
                elif 31 <= percentage <= 67:
                    return 0  # Suspicious
                else:
                    return -1  # Phishing
            return 1
        except:
            return 1
    
    def links_in_tags(self):
        """Feature 15: Links in meta, script, and link tags"""
        try:
            if self.soup:
                links = 0
                external_links = 0
                
                for tag in self.soup.find_all(['meta', 'script', 'link']):
                    for attr in ['href', 'src', 'content']:
                        url = tag.get(attr, '')
                        if url and url.startswith('http'):
                            links += 1
                            if self.domain not in url:
                                external_links += 1
                
                if links > 0:
                    percentage = (external_links / links) * 100
                    if percentage < 17:
                        return 1  # Legitimate
                    elif 17 <= percentage <= 81:
                        return 0  # Suspicious
                    else:
                        return -1  # Phishing
            return 1
        except:
            return 1
    
    def sfh(self):
        """Feature 16: Server Form Handler"""
        try:
            if self.soup:
                forms = self.soup.find_all('form')
                if len(forms) == 0:
                    return 1  # No forms
                
                for form in forms:
                    action = form.get('action', '')
                    if action == '' or action == 'about:blank':
                        return -1  # Phishing
                    elif action.startswith('http') and self.domain not in action:
                        return 0  # Suspicious
                return 1  # Legitimate
            return 1
        except:
            return 1
    
    def submitting_to_email(self):
        """Feature 17: Check if form submits to email"""
        try:
            if self.soup:
                forms = self.soup.find_all('form')
                for form in forms:
                    action = form.get('action', '').lower()
                    if 'mailto:' in action or 'mail(' in action:
                        return -1  # Phishing
                return 1  # Legitimate
            return 1
        except:
            return 1
    
    def abnormal_url(self):
        """Feature 18: Check if hostname is in URL"""
        try:
            domain_info = whois.whois(self.domain)
            if domain_info and hasattr(domain_info, 'domain_name'):
                if isinstance(domain_info.domain_name, list):
                    domain_name = domain_info.domain_name[0].lower()
                else:
                    domain_name = domain_info.domain_name.lower()
                
                if domain_name in self.url.lower():
                    return 1  # Legitimate
            return -1  # Phishing
        except:
            return -1
    
    def redirect(self):
        """Feature 19: Number of redirects"""
        try:
            response = requests.get(self.url, timeout=self.timeout, allow_redirects=True)
            redirects = len(response.history)
            if redirects <= 1:
                return 1  # Legitimate
            elif redirects <= 4:
                return 0  # Suspicious
            else:
                return -1  # Phishing
        except:
            return -1
    
    def on_mouseover(self):
        """Feature 20: Check for onMouseOver to hide link"""
        try:
            if self.soup:
                if self.html_content and 'onmouseover' in self.html_content.lower():
                    return -1  # Phishing
                return 1  # Legitimate
            return 1
        except:
            return 1
    
    def right_click(self):
        """Feature 21: Check if right-click is disabled"""
        try:
            if self.soup:
                patterns = [
                    'event.button==2',
                    'event.button == 2',
                    'contextmenu',
                    'event.button==3',
                    'event.button == 3'
                ]
                for pattern in patterns:
                    if pattern in self.html_content.lower():
                        return -1  # Phishing
                return 1  # Legitimate
            return 1
        except:
            return 1
    
    def popup_window(self):
        """Feature 22: Check for pop-up windows"""
        try:
            if self.soup:
                if 'window.open(' in self.html_content or 'popup' in self.html_content.lower():
                    return -1  # Phishing
                return 1  # Legitimate
            return 1
        except:
            return 1
    
    def iframe(self):
        """Feature 23: Check for iframe usage"""
        try:
            if self.soup:
                iframes = self.soup.find_all('iframe')
                if len(iframes) > 0:
                    return -1  # Phishing
                return 1  # Legitimate
            return 1
        except:
            return 1
    
    def age_of_domain(self):
        """Feature 24: Age of domain"""
        try:
            domain_info = whois.whois(self.domain)
            if domain_info.creation_date:
                if isinstance(domain_info.creation_date, list):
                    creation_date = domain_info.creation_date[0]
                else:
                    creation_date = domain_info.creation_date
                
                age = (datetime.now() - creation_date).days
                if age >= 180:  # 6 months
                    return 1  # Legitimate
                else:
                    return -1  # Phishing
            return -1
        except:
            return -1
    
    # ==================== DOMAIN AND WEBSITE TRAFFIC FEATURES (25-30) ====================
    
    def dns_record(self):
        """Feature 25: Check DNS record"""
        try:
            dns.resolver.resolve(self.domain, 'A')
            return 1  # Legitimate
        except:
            return -1  # Phishing
    
    def web_traffic(self):
        """Feature 26: Check website traffic (simplified)"""
        # Note: Alexa rank is deprecated, you may need to use alternatives
        try:
            # Placeholder - you can integrate with Similarweb API or other traffic analysis
            # For now, return neutral
            return 0
        except:
            return -1
    
    def page_rank(self):
        """Feature 27: Google PageRank (simplified)"""
        # Note: Google PageRank is deprecated
        # Placeholder implementation
        try:
            return 0  # Neutral
        except:
            return -1
    
    def google_index(self):
        """Feature 28: Check if indexed by Google"""
        try:
            url = f"https://www.google.com/search?q=site:{self.domain}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=self.timeout)
            if 'did not match any documents' in response.text:
                return -1  # Phishing
            return 1  # Legitimate
        except:
            return -1
    
    def links_pointing_to_page(self):
        """Feature 29: Number of backlinks (simplified)"""
        # This would require integration with SEO APIs
        # Placeholder implementation
        try:
            return 0  # Neutral
        except:
            return -1
    
    def statistical_report(self):
        """Feature 30: Based on PhishTank/APWG reports"""
        # This would require integration with PhishTank API
        # Placeholder implementation
        try:
            return 1  # Assume legitimate unless found in database
        except:
            return 1


# Example usage
if __name__ == "__main__":
    # Test with a URL
    test_url = "https://www.google.com"
    
    extractor = URLFeatureExtractor(test_url)
    features = extractor.extract_all_features()
    
    print("Extracted Features:")
    print("=" * 50)
    for idx, (feature_name, value) in enumerate(features.items(), 1):
        print(f"{idx}. {feature_name}: {value}")
    
    print("\n" + "=" * 50)
    print(f"Total features extracted: {len(features)}")
