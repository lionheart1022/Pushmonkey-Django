from clients.models import ClientProfile

clients = ClientProfile.objects.filter(confirmed = True, status = "active")

ClientProfile.objects.filter(confirmed = True, status = "active").count()

"confirmed clients with push packages assigned": 373

ClientProfile.objects.count()

"total people subscribed": 1540

ClientProfile.objects.filter(status = "pending").count()

"total people w/o push packages": 879

===

from pushmonkey.models import PushMessage
from django.db.models import Count
from datetime import datetime, timedelta
past_date = datetime.now() - timedelta(days = 90)
PushMessage.objects.filter(created_at__gt = past_date).values('account_key').annotate(Count('account_key'))

PushMessage.objects.filter(created_at__gt = past_date).values('account_key').annotate(Count('account_key'))

"number of accounts that sent a notification in the past 90 days": 83

==

number_of_top = 83
top = PushMessage.objects.filter(created_at__gt = past_date).values('account_key').annotate(notifications_sent = Count('account_key')).order_by("-notifications_sent")[:number_of_top]
top_clients = ClientProfile.objects.filter(account_key__in = [t["account_key"] for t in top]).values("user__email", "website", "account_key")
top_clients_sorted = sorted(top_clients, key = lambda c: -[x for x in top if x["account_key"] == c["account_key"]][0]["notifications_sent"])
for c in top_clients_sorted:
  print(c["website"], c["user__email"], c["account_key"], [x for x in top if x["account_key"] == c["account_key"]][0]["notifications_sent"])

"top 83 profiles:"
(u'http://hbtvghana.com/', u'medivals2006@gmail.com', u'0LI6P4EOZS9F28AND', 630)
(u'http://www.myonlinemagazine.com/', u'healthyfoodandremedies@gmail.com', u'3S6N5QYDA4C2BMHP9', 556)
(u'http://www.socialup.it/', u'redazione@socialup.it', u'DT5PE37Z9GNFRO2M4', 490)
(u'http://streetregister.com/', u'mark@streetnewswire.com', u'IJCBOG97N3PYK5RMS', 227)
(u'http://portalcanaa.com.br/', u'jorgepebas@gmail.com', u'JI6Q8OWZ5AXRN9M2P', 161)
(u'http://www.sensaciondeportiva.com/', u'cristian@eosmediacr.com', u'46SP8U3DALWJGI9V5', 154)
(u'http://radargamer.com/', u'rafael@radargamer.com', u'9EYIJ1XDG3KU7FZ80', 154)
(u'http://www.revoltabrasil.com.br/', u'juniorjuridico@live.com', u'EK073S4JZ5YHFWN2V', 144)
(u'http://www.vagascomunicacao.com/', u'contato@vagascomunicacao.com', u'OW0HGI3LR4AJV7N6F', 141)
(u'http://burgasdaily.com/', u'burgasdaily@abv.bg', u'3NWVIUFLK9J4C2S50', 138)
(u'http://otcnewsmagazine.com/', u'stock_talk101@yahoo.com', u'2N56VDX73RMW0GKEL', 127)
(u'http://funkyspacemonkey.com/', u'murdamw@gmail.com', u'VXLDZNEQSGI0J981C', 82)
(u'http://www.canabravafm.com.br/2/home.htm', u'ti@cleissoncardoso.com', u'Q7JOXE9C528WI4UF1', 78)
(u'http://www.esportecampeao.com/', u'contato@esportecampeao.com', u'4XPB3EZN97HRD0WMQ', 58)
(u'http://sp-bx.com/', u'editor@sp-bx.com', u'NCJO57PAGU01S3DYX', 48)
(u'http://careeryaan.com/', u'careeryaan@gmail.com', u'UVAFCRLM305EG4DJT', 48)
(u'http://www.gadgetlite.in/', u'pogoshank@gmail.com', u'QI58NLGJOZ936B4W0', 39)
(u'https://wptest-pushmonkey.rhcloud.com/', u'akchirpy@gmail.com', u'LGD5MFJ4Q6CPKI3RH', 34)
(u'http://technomela.net/', u'danielericcardi@gmail.com', u'L9W3PRN6JAH80GZ4V', 30)
(u'https://getpushmonkey.com/', u'tmunteanu@thinkful.com', u'CW598XLRMJ3YUBTZI', 27)
(u'http://www.councilestate.co.uk/', u'skintdeals@gmail.com', u'4SW6NJY1BDEOR309H', 27)
(u'https://www.insiderfinancial.com/', u'streetnewswire22@gmail.com', u'19T5087SE42CPYB6U', 25)
(u'http://notisia.woworibabo.com/', u'woworibabo@gmail.com', u'BCNYFQMA6GDTZEI1R', 23)
(u'http://blog.mypage.vn/', u'taibuivnn@gmail.com', u'X69E8IFVDJ1RPM0LO', 23)
(u'http://www.tudochinaexpress.com/', u'gomesfabr@gmail.com', u'7KVHZL59CX1ASUI3O', 21)
(u'http://www.ruvesi.it/', u'ufficiostampa@ruvochannel.com', u'GZOFEVHPR9I510Y7D', 19)
(u'https://overpassesforamerica.com/', u'matlefebvre2010@att.net', u'W59CMXGSIUEZLNJKP', 17)
(u'https://szifon.com/', u'hello@szifon.com', u'K17W5HDVUJ3ZOP4RI', 15)
(u'http://ithinkdiff.com/', u'imran@ithinkdiff.com', u'XC4J5MAYPGI92ZOVR', 13)
(u'http://adammclane.com/', u'mclanea@gmail.com', u'dcf6112638fab42e9b8f0e4b81f12cca765433a32ea7ed6ec736580a', 12)
(u'http://www.shoutmakersdream.com/', u'factswithme@gmail.com', u'TYLJP2KH801CUXVFN', 11)
(u'http://www.institutoovidiomachado.org/', u'pugnaloni@gmail.com', u'G801M7EWJPOIHQCYS', 9)
(u'https://kloopkg.staging.wpengine.com/', u'diamant0408@gmail.com', u'8YTBEUXA7IS0P2ZGN', 8)
(u'http://www.journaltranscript.com/', u'mailmythought@gmail.com', u'A367DW2MR84STQOC0', 7)
(u'http://batuhanilgar.com/', u'batuhan@batuhanilgar.com', u'QFK7VM4NREOAYX30W', 7)
(u'https://uoftastemagazine.com/', u'mspikesjr@gmail.com', u'V3415PDBQ7NXHLFAK', 7)
(u'http://appleusergroupresources.com/', u'ugab@mac.com', u'XJIG6239Q807SK54R', 6)
(u'https://www.racingvalue.com/', u'djdamien@hotmail.com', u'EB8HT6L1VRXZDQFJ9', 6)
(u'http://www.fondosbitcoin.com/', u'viceroid@gmail.com', u'IZHPMQDNGE3TL8KO7', 6)
(u'http://state-lines.com/', u'atomkappel@gmail.com', u'UVSE24X75MAFQPZYI', 5)
(u'http://www.storyheros.com/', u'letters@storyheros.com', u'OGNR37JPI5VWDMXUH', 5)
(u'http://www.tweesnoeken.nl/', u'robbie.van.den.hoven@tweesnoeken.nl', u'PVA4B7HC6J1XW80QG', 5)
(u'http://www.manilatouch.com/', u'admin@manilatouch.com', u'QYPR3KEC2H51A7X0L', 5)
(u'https://www.mihaivasiloiu.ro/', u'bartok.gabi17@gmail.com', u'BUIH51ZAR8PN0YOTF', 5)
(u'http://liberal.ns.ca/', u'scott@boom12.ca', u'1L0CITA5J4YMZDRVE', 5)
(u'http://www.writid.net/', u'writid08@gmail.com', u'AU0XNRBDMV8HP3KTQ', 4)
(u'http://theride.a8d.in/', u'nazrul@wowevents.in', u'MRHCAY9E1GTJ8SVN6', 4)
(u'http://thinkbusinessfinance.co.uk/', u'danny.brand@thinkbusinessfinance.co.uk', u'6890SKIZJ3FYLGO57', 4)
(u'http://darylbaxter.com/', u'contact@darylbaxter.com', u'I6UH91K2MZVGEJOD3', 4)
(u'https://www.sitisocialweb.com/', u'sitisocialweb@gmail.com', u'1E9PVCRBLAO7HM534', 4)
(u'http://xfer.cybussolutions.com/klutchit', u'fahim.akhtar@cybussolutions.com', u'5D7R4YWAJHXP8FTZB', 3)
(u'http://mydrtest.infoconnekt.com/', u'eniyan.45@gmail.com', u'2Q9V5URHZIC4S1MA0', 3)
(u'http://www.argusjournal.com/', u'alokkhand@gmail.com', u'EQC0YBI3FJV2XMKPD', 3)
(u'https://localhost/wpdev', u'kyle.egan@coact.org.au', u'8ISXFQWUZOBRT4MPH', 3)
(u'http://www.euskalgrooves.com/', u'euskalgrooves@gmail.com', u'W2T6S9V7K1D54HAJZ', 2)
(u'http://messiahsmandate.org/', u'roncan@me.com', u'MFGCJPN9S3BV5E2YI', 2)
(u'http://www.kreativnoir.co.za/', u'paul@kreativnoir.co.za', u'TNVYBSG6KHUCD4O2Z', 2)
(u'http://careerdubai.com/', u'mt@careerdubai.net', u'GK8WHFRZ9IE4V21QX', 2)
(u'http://www.sammaer.com/', u'sifisogonya011@gmail.com', u'CTXYR2IH3DEV6J0O1', 2)
(u'http://betkoks.dx.am/', u'l1688591@mvrht.com', u'ROX54EJG2YCKQIVU8', 2)
(u'https://moldovacrestina.md/', u'filatdav@gmail.com', u'ZE72801GVUKRST946', 2)
(u'http://www.en-media.tv/', u'mc.energodar@gmail.com', u'DH4RSY8A9MT0O65NQ', 2)
(u'http://stlucianewsnow.net/', u'stlucianewsnow1@gmail.com', u'IGUTWSOV6JKR81XEQ', 2)
(u'http://horoscopodia.virgula.uol.com.br/', u'fcondutta@gmail.com', u'TAZ3IJQL58GWOUNHF', 1)
(u'https://www.amzdealsclub.us/', u'sales@reviewsforfree.com', u'FI2RZTHKN6A83GLCY', 1)
(u'https://wallstreetpr.com/', u'khandalok@gmail.com', u'JW68MDH47XOUQIC9L', 1)
(u'http://iasbla.org/IAS', u'support@iasbla.org', u'KZNOWHM4P78YQSU2A', 1)
(u'http://compuleb.org/', u'marwan.wehbe7@gmail.com', u'3IAM9C8QPXJ2OZEBU', 1)
(u'https://www.laguiadesincelejo.com/', u'info@sabanaurbana.com.co', u'3KQUGP6E2WDBHVF8M', 1)
(u'http://www.pascalkramer.com/', u'info@pascalkramer.com', u'8OC976NS41FHUE0DZ', 1)
(u'https://niaou.net/', u'hrenos@gmail.com', u'SX7PNWOTVIL350KFJ', 1)
(u'https://www.spotdiecontrole.nl/', u'info@spotdiecontrole.nl', u'ORV3YASQ0BC4D9I2E', 1)
(u'http://mydrnew.infoconnekt.com/', u'eniyansrirangam@gmail.com', u'BECY7S6NQ94A2PWLI', 1)
(u'http://www.midialab.org/a25', u'telesmaneira1@gmail.com', u'OIPSCG1AM459YU36X', 1)
(u'https://royalty-market.com/', u'yanis.halios@gmail.com', u'8Y6HBDGNUOMAJI2KX', 1)
(u'http://weslyweblink.esy.es/', u'wesly@weblink.com.br', u'TBI529PYX3DFGNZQV', 1)
(u'http://jurisaprendiz.com.br/', u'companyfischers@gmail.com', u'B2N5OVP7GTCY6AD3K', 1)
(u'http://172.16.16.116/testrestapi', u'l2986385@mvrht.com', u'I37DV6CO2BJULFPQW', 1)
(u'http://www.scriptyeri.com/', u'grafikbursa@gmail.com', u'W1N89AR6X0MLIZS5P', 1)
(u'https://selfhelp.institute/', u'hawk@selfhelp.institute', u'EV6RCFHDS9GQ4XUKZ', 1)
(u'http://revistamenteativa.com.br/', u'jeferson.jreis@icloud.com', u'83ZFOBPXV5UKM9JLS', 1)
