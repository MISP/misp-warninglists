#!/usr/bin/env python3
import multiprocessing.dummy
from generator import get_version, write_to_file, Dns, consolidate_networks, create_resolver

# Source: https://github.com/mailcheck/mailcheck/wiki/List-of-Popular-Domains
domains = [
    # Default domains included
    "aol.com", "att.net", "comcast.net", "facebook.com", "gmail.com", "gmx.com", "googlemail.com",
    "google.com", "hotmail.com", "hotmail.co.uk", "mac.com", "me.com", "mail.com", "msn.com",
    "live.com", "sbcglobal.net", "verizon.net", "yahoo.com", "yahoo.co.uk",

    # Other global domains
    "email.com", "fastmail.fm", "games.com", "gmx.net", "hush.com", "hushmail.com", "icloud.com",
    "iname.com", "inbox.com", "lavabit.com",
    "love.com", "outlook.com", "pobox.com", "protonmail.ch", "protonmail.com", "tutanota.de", "tutanota.com",
    "tutamail.com", "tuta.io",
    "keemail.me", "rocketmail.com", "safe-mail.net", "wow.com", "ygm.com",
    "ymail.com", "zoho.com", "yandex.com",

    # United States ISP domains
    "bellsouth.net", "charter.net", "cox.net", "earthlink.net", "juno.com",

    # British ISP domains
    "btinternet.com", "virginmedia.com", "blueyonder.co.uk", "live.co.uk",
    "ntlworld.com", "orange.net", "sky.com", "talktalk.co.uk", "tiscali.co.uk",
    "virgin.net", "bt.com",

    # Domains used in Asia
    "sina.com", "sina.cn", "qq.com", "naver.com", "hanmail.net", "daum.net", "nate.com", "yahoo.co.jp", "yahoo.co.kr",
    "yahoo.co.id", "yahoo.co.in", "yahoo.com.sg", "yahoo.com.ph", "163.com", "yeah.net", "126.com", "21cn.com",
    "aliyun.com", "foxmail.com",

    # French ISP domains
    "hotmail.fr", "live.fr", "laposte.net", "yahoo.fr", "wanadoo.fr", "orange.fr", "gmx.fr", "sfr.fr", "neuf.fr",
    "free.fr",

    # German ISP domains
    "gmx.de", "hotmail.de", "live.de", "online.de", "t-online.de", "web.de", "yahoo.de",

    # Italian ISP domains
    "libero.it", "virgilio.it", "hotmail.it", "aol.it", "tiscali.it",
    "alice.it", "live.it", "yahoo.it", "email.it", "tin.it", "poste.it", "teletu.it",

    # Russian ISP domains
    "bk.ru", "inbox.ru", "list.ru", "mail.ru", "rambler.ru", "yandex.by", "yandex.com", "yandex.kz", "yandex.ru",
    "yandex.ua", "ya.ru",

    # Belgian ISP domains
    "hotmail.be", "live.be", "skynet.be", "voo.be", "tvcablenet.be", "telenet.be",

    # Argentinian ISP domains
    "hotmail.com.ar", "live.com.ar", "yahoo.com.ar", "fibertel.com.ar", "speedy.com.ar", "arnet.com.ar",

    # Domains used in Mexico
    "yahoo.com.mx", "live.com.mx", "hotmail.es", "hotmail.com.mx", "prodigy.net.mx",

    # Domains used in Canada
    "yahoo.ca", "hotmail.ca", "bell.net", "shaw.ca", "sympatico.ca", "rogers.com",

    # Domains used in Brazil
    "yahoo.com.br", "hotmail.com.br", "outlook.com.br", "uol.com.br", "bol.com.br", "terra.com.br", "ig.com.br",
    "r7.com", "zipmail.com.br", "globo.com", "globomail.com", "oi.com.br",

    # Custom extension
    # Domains used in Czechia
    "seznam.cz", "atlas.cz", "centrum.cz",
]


if __name__ == '__main__':
    dns = Dns(create_resolver())

    spf_ranges = []
    p = multiprocessing.dummy.Pool(40)
    for domain_ranges in p.map(lambda d: dns.get_ip_ranges_from_spf(d), domains):
        spf_ranges.extend(domain_ranges)

    warninglist = {
        'name': "List of known SMTP sending IP ranges",
        'version': get_version(),
        'description': "List of IP ranges for known SMTP servers.",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr',
        'list': consolidate_networks(spf_ranges),
    }
    write_to_file(warninglist, "smtp-sending-ips")

    mx_ips = []
    for domain_ranges in p.map(lambda d: dns.get_mx_ips_for_domain(d), domains):
        mx_ips.extend(domain_ranges)

    warninglist = {
        'name': "List of known SMTP receiving IP addresses",
        'version': get_version(),
        'description': "List of IP addresses for known SMTP servers.",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr',
        'list': map(str, mx_ips),
    }
    write_to_file(warninglist, "smtp-receiving-ips")
