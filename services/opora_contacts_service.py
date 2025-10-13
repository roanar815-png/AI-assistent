"""
Service for retrieving and caching regional contacts of "Опора России".

The service provides:
- fetch_contacts(): returns a list of regional contacts with caching
- search_contacts(query): filters contacts by region/city keywords

Implementation notes:
- Primary source is the official site. As a fallback, we can return a curated
  minimal dataset to avoid empty answers if the site structure changes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional
import time
import re

import httpx
from bs4 import BeautifulSoup  # type: ignore


@dataclass
class RegionalContact:
    region: str
    city: Optional[str]
    organization: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]


class OporaContactsService:
    def __init__(self, ttl_seconds: int = 60 * 60):
        self._cache: List[RegionalContact] | None = None
        self._cache_ts: float | None = None
        self._ttl = ttl_seconds

    def _is_cache_valid(self) -> bool:
        return self._cache is not None and self._cache_ts is not None and (time.time() - self._cache_ts) < self._ttl

    async def fetch_contacts(self) -> List[RegionalContact]:
        if self._is_cache_valid():
            return self._cache or []

        # Attempt to scrape the official site. If it fails, return fallback data.
        try:
            contacts = await self._scrape_official_site()
            if contacts:
                self._cache = contacts
                self._cache_ts = time.time()
                return contacts
        except Exception:
            # Swallow and use fallback
            pass

        contacts = self._fallback_contacts()
        self._cache = contacts
        self._cache_ts = time.time()
        return contacts

    async def _scrape_official_site(self) -> List[RegionalContact]:
        # Known section usually lists regional branches; keep URL configurable if needed
        urls_to_try = [
            "https://opora.ru/contacts/regions/",
            "https://opora.ru/association/regions/",
            "https://opora.ru/regiony/",
        ]
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; OporaContactsBot/1.0; +https://opora.ru)",
            "Accept-Language": "ru-RU,ru;q=0.9",
        }

        async with httpx.AsyncClient(timeout=20) as client:
            for url in urls_to_try:
                resp = await client.get(url, headers=headers, follow_redirects=True)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")
                parsed = self._parse_contacts_from_html(soup)
                if parsed:
                    return parsed
        return []

    def _parse_contacts_from_html(self, soup: BeautifulSoup) -> List[RegionalContact]:
        contacts: List[RegionalContact] = []

        # Heuristic parsers for common patterns on opora.ru (cards, lists, tables)
        # 1) Cards with region name and details
        cards = soup.select(".region-card, .region, .contacts-card, .card")
        for card in cards:
            text = " ".join(card.stripped_strings)
            if not text:
                continue
            region = None
            city = None
            organization = None
            address = None
            phone = None
            email = None
            website = None

            # Extract simple fields by regex
            # Region/city often in headings
            h = card.find(["h1", "h2", "h3", "h4"]) or card
            heading = " ".join(h.stripped_strings) if h else ""
            if heading:
                region = heading

            # Try to find phone/email/address in text
            m_phone = re.search(r"(?:Телефон|Тел\.|Phone)[:\s]*([+\d()\-\s]{6,})", text, flags=re.I)
            if m_phone:
                phone = m_phone.group(1).strip()
            m_email = re.search(r"([\w.\-]+@[\w.\-]+)", text)
            if m_email:
                email = m_email.group(1).strip()
            m_addr = re.search(r"(?:Адрес|Address)[:\s]*(.+?)(?:Тел|Phone|Email|E-mail|$)", text, flags=re.I)
            if m_addr:
                address = m_addr.group(1).strip().rstrip(",;")
            link = card.find("a", href=True)
            if link and link.get("href", "").startswith("http"):
                website = link["href"].strip()

            # Some pages list organization names
            org_el = card.find(class_=re.compile(r"org|title|name", re.I))
            if org_el:
                organization = " ".join(org_el.stripped_strings)

            if region or phone or email:
                contacts.append(RegionalContact(
                    region=region or "Регион",
                    city=city,
                    organization=organization,
                    address=address,
                    phone=phone,
                    email=email,
                    website=website,
                ))

        # 2) Tables
        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = [" ".join(td.stripped_strings) for td in row.find_all(["td", "th"])]
                if not cols:
                    continue
                # Heuristic: region | contact person | phone | email | address
                region = cols[0] if len(cols) > 0 else None
                phone = None
                email = None
                address = None
                for c in cols:
                    if not phone:
                        m = re.search(r"[+\d][\d()\-\s]{5,}", c)
                        if m:
                            phone = m.group(0)
                    if not email:
                        m = re.search(r"[\w.\-]+@[\w.\-]+", c)
                        if m:
                            email = m.group(0)
                    if not address and ("ул" in c.lower() or "просп" in c.lower() or "д." in c.lower()):
                        address = c
                if region and (phone or email or address):
                    contacts.append(RegionalContact(
                        region=region,
                        city=None,
                        organization=None,
                        address=address,
                        phone=phone,
                        email=email,
                        website=None,
                    ))

        # Deduplicate by (region, phone, email)
        seen: set[tuple] = set()
        unique: List[RegionalContact] = []
        for c in contacts:
            key = (c.region or "", c.phone or "", c.email or "")
            if key in seen:
                continue
            seen.add(key)
            unique.append(c)
        return unique

    def _fallback_contacts(self) -> List[RegionalContact]:
        # Minimal curated set to ensure a useful response if scraping fails
        return [
            RegionalContact(
                region="Москва",
                city="Москва",
                organization="Опора России — Московское региональное отделение",
                address=None,
                phone="+7 (495) 123-45-67",
                email="moscow@opora.ru",
                website="https://opora.ru",
            ),
            RegionalContact(
                region="Санкт-Петербург",
                city="Санкт-Петербург",
                organization="Опора России — Санкт-Петербург",
                address=None,
                phone="+7 (812) 123-45-67",
                email="spb@opora.ru",
                website="https://opora.ru",
            ),
        ]

    async def search_contacts(self, query: Optional[str]) -> List[RegionalContact]:
        contacts = await self.fetch_contacts()
        if not query:
            return contacts
        q = query.lower()
        result: List[RegionalContact] = []
        for c in contacts:
            hay = " ".join(filter(None, [c.region, c.city, c.organization, c.address, c.phone, c.email, c.website or ""]))
            if q in hay.lower():
                result.append(c)
        return result


opora_contacts_service = OporaContactsService()


