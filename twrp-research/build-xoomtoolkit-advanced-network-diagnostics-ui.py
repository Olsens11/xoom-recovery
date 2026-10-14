#!/usr/bin/env python3
"""Build future Network Diagnostics 0.2.0 detail-page fragment, not R22d4c."""
from pathlib import Path
import xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
OUT=HERE/"XoomToolkit-Advanced-Network-Diagnostics-0.2.0-FUTURE-TWRP-page.xml"
assert not OUT.exists(), "Refuse overwrite; initial template creation only"
root=ET.Element("future_toolkit_pages")
page=ET.SubElement(root,"page",{"name":"xoom_toolkit_details_diag"})
ET.SubElement(page,"template",{"name":"page"})
start=ET.SubElement(page,"action")
ET.SubElement(start,"action",{"function":"xoomtoolkit"}).text="network-diag-refresh"
def label(content,x,y,font="font_m",color="%text_color%"):
    el=ET.SubElement(page,"text")
    ET.SubElement(el,"placement",{"x":str(x),"y":str(y)})
    ET.SubElement(el,"font",{"resource":font,"color":color})
    ET.SubElement(el,"text").text=content
def button(title,x,y,w,destination,fn,color="#264e7c"):
    el=ET.SubElement(page,"button")
    ET.SubElement(el,"placement",{"x":str(x),"y":str(y),"w":str(w),"h":"72"})
    ET.SubElement(el,"fill",{"color":color})
    ET.SubElement(el,"font",{"resource":"font_m","color":"#ffffff"})
    ET.SubElement(el,"text").text=title
    ET.SubElement(el,"action",{"function":fn}).text=destination
label("Network Diagnostics",81,187,font="font_l")
label("Recovery Wi-Fi, routing and DNS health",81,274,color="%accent_color%")
rows=[
 ("Report: %xt_diag_status%   Wi-Fi: %xt_diag_wifi_state%",351),
 ("WPA authentication: %xt_diag_wpa_auth%",410),
 ("Local IPv4: %xt_diag_ipv4%",467),
 ("Default gateway: %xt_diag_gateway%",524),
 ("DNS server: %xt_diag_dns_server%   Proxy: %xt_diag_dns_proxy%",581),
 ("Public ICMP: %xt_diag_probe_internet%",637),
 ("DNS A query: %xt_diag_probe_dns%",693),
]
for t,y in rows:label(t,81,y)
label("Probe failures may indicate filtering, not necessarily a network fault.",81,756,font="font_s")
for title,x,fn,dest in [
 ("Inspect Network",81,"xoomtoolkitexec","start:network-diagnostics"),
 ("Test Connectivity",463,"xoomtoolkitexec","test:network-diagnostics"),
 ("Export Report",845,"xoomtoolkitexec","export:network-diagnostics"),
 ("Refresh Status",1227,"xoomtoolkit","network-diag-refresh")
]:
    button(title,x,840,350,dest,fn,color="#216d99" if x<845 else "#264e7c")
button("Back to Toolkit",1440,1050,370,"xoom_toolkit","page")
back=ET.SubElement(page,"action")
ET.SubElement(back,"touch",{"key":"back"})
ET.SubElement(back,"action",{"function":"page"}).text="xoom_toolkit"
tree=ET.ElementTree(root)
ET.indent(tree,space="  ")
tree.write(OUT,encoding="utf-8",xml_declaration=True)
print("NETWORK_DIAGNOSTICS_FUTURE_UI_STAGED",OUT.name)
