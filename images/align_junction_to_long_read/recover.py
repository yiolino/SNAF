#!/data/salomonis2/LabFiles/Frank-Li/refactor/neo_env/bin/python3.7

import os
import sys
sys.path.insert(0,'/data/salomonis2/software')
import snaf
from snaf import surface
import pandas as pd
import numpy as np
import anndata as ad
import pickle
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
import subprocess

import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'Arial'


# get reduced junction
df = snaf.get_reduced_junction_matrix(pc='../TCGA_melanoma/counts.TCGA-SKCM.txt',pea='../TCGA_melanoma/Hs_RNASeq_top_alt_junctions-PSI_EventAnnotation.txt')

# run SNAF
netMHCpan_path = '/data/salomonis2/LabFiles/Frank-Li/refactor/external/netMHCpan-4.1/netMHCpan'
db_dir = '/data/salomonis2/LabFiles/Frank-Li/neoantigen/revision/data'
tcga_ctrl_db = ad.read_h5ad(os.path.join(db_dir,'controls','tcga_matched_control_junction_count.h5ad'))
gtex_skin_ctrl_db = ad.read_h5ad(os.path.join(db_dir,'controls','gtex_skin_count.h5ad'))
add_control = {'tcga_control':tcga_ctrl_db,'gtex_skin':gtex_skin_ctrl_db}

snaf.initialize(df=df,db_dir=db_dir,binding_method='netMHCpan',software_path=netMHCpan_path,add_control=add_control)
surface.initialize(db_dir=db_dir)

# given a uid and gtf, return full_length isoform
uid = 'ENSG00000218336:E1.1-E4.1'
gtf_path = '/data/salomonis2/LabFiles/Frank-Li/refactor/data/2021UHRRIsoSeq_SQANTI3_filtered.gtf'

gtf_dict = surface.main.process_est_or_long_read_with_id(gtf_path)
sa = surface.SurfaceAntigen(uid=uid,
                            score=None,
                            df=None,
                            ed=None,
                            freq=None,
                            check_overlap=False)
sa.detect_type()
sa.retrieve_junction_seq()
sa.recovery_full_length_protein_long_read(gtf_dict) 
sa.find_orf()
sa.pseudo_orf_check()  
print(sa)
print(sa.orfp)
print(sa.full_length_attrs)


'''
uid:ENSG00000218336:E1.1-E4.1
scores and freqs:None,None
comments:[]
event type:ordinary
Junction:AAAAA...ACAAG
Full length transcripts: length 3, indices [0, 1, 2]
ORF transcripts: length 3, indices [0, 1, 2]
ORF peptides: length 3, indices [0, 1, 2]
NMD check: length 3, indices ['#', '#', '#']
tranlatability check: length 3, indices ['#', '#', '#']
Alignment: length None, indices None

['MDVKERRPYCSLTKSRREKERRYTNSSADNEECRVPTQKSYSSSETLKAFDHDSSRLLYGNRVKDLVHREADEFTRQGQNFTLRQLGVCEPATRRGLAFCAEMGLPHRGYSISAGSDADTENEAVMSPEHAMRLWGRGVKSGRSSCLSSRSNSALTLTDTEHENKSDSENEQPASNQGQSTLQPLPPSHKQHSAQHHPSITSLNRNSLTNRRNQSPAPPAALPAELQTTPESVQLQDSWVLGSNVPLESRHFLFKTGTGTTPLFSTATPGYTMASGSVYSPPTRPLPRNTLSRSAFKFKKSSKYCSWKCTALCAVGVSVLLAILLSYFIAMHLFGLNWQLQQTENDTFENGKVNSDTMPTNTVSLPSGDNGKLGGFTQENNTIDSGELDIGRRAIQEIPPGIFWRSQLFIDQPQFLKFNISLQKDALIGVYGRKGLPPSHTQYDFVELLDGSRLIAREQRSLLETERAGRQARSVSLHEAGFIQYLDSGIWHLAFYNDGKNAEQVSFNTIVIESVVECPRNCHGNGECVSGTCHCFPGFLGPDCSRAACPVLCSGNGQYSKGRCLCFSGWKGTECDVPTTQCIDPQCGGRGICIMGSCACNSGYKGESCEEADCIDPGCSNHGVCIHGECHCSPGWGGSNCEILKTMCPDQCSGHGTYLQESGSCTCDPNWTGPDCSNEICSVDCGSHGVCMGGTCRCEEGWTGPACNQRACHPRCAEHGTCKDGKCECSQGWNGEHCTIEGCPGLCNSNGRCTLDQNGWHCVCQPGWRGAGCDVAMETLCTDSKDNEGDGLIDCMDPDCCLQSSCQNQPYCRGLPDPQDIISQSLQSPSQQAAKSFYDRISFLIGSDSTHVIPGESPFNKSLASVIRGQVLTADGTPLIGVNVSFFHYPEYGYTITRQDGMFDLVANGGASLTLVFERSPFLTQYHTVWIPWNVFYVMDTLVMKKEENDIPSCDLSGFVRPNPIIVSSPLSTFFRSSPEDSPIIPETQVLHEETTIPGTDLKLSYLSSRAAGYKSVLKITMTQSIIPFNLMKVHLMVAVVGRLFQKWFPASPNLAYTFIWDKTDAYNQKVYGLSEAVVSVGYEYESCLDLTLWEKRTAILQGYELDASNMGGWTLDKHHVLDVQNGILYKGNGENQFISQQPPVVSSIMGNGRRRSISCPSCNGQADGNKLLAPVALACGIDGSLYVGDFNYVRRIFPSGNVTSVLELSSNPAHRYYLATDPVTGDLYVSDTNTRRIYRPKSLTGAKDLTKNAEVVAGTGEQCLPFDEARCGDGGKAVEATLMSPKGMAVDKNGLIYFVDGTMIRKVDQNGIISTLLGSNDLTSARPLTCDTSMHISQVRLEWPTDLAINPMDNSIYVLDNNVVLQITENRQVRIAAGRPMHCQVPGVEYPVGKHAVQTTLESATAIAVSYSGVLYITETDEKKINRIRQVTTDGEISLVAGIPSECDCKNDANCDCYQSGDGYAKDAKLSAPSSLAASPDGTLYIADLGNIRIRAVSKNKPLLNSMNFYEVASPTDQELYIFDINGTHQYTVSLVTGDYLYNFSYSNDNDITAVTDSNGNTLRIRRDPNRMPVRVVSPDNQVIWLTIGTNGCLKSMTAQGLELVLFTYHGNSGLLATKSDETGWTTFFE', 'MDVKERRPYCSLTKSRREKERRYTNSSADNEECRVPTQKSYSSSETLKAFDHDSSRLLYGNRVKDLVHREADEFTRQGQNFTLRQLGVCEPATRRGLAFCAEMGLPHRGYSISAGSDADTENEAVMSPEHAMRLWGRGVKSGRSSCLSSRSNSALTLTDTEHENKSDSENEQPASNQGQSTLQPLPPSHKQHSAQHHPSITSLNRNSLTNRRNQSPAPPAALPAELQTTPESVQLQDSWVLGSNVPLESRHFLFKTGTGTTPLFSTATPGYTMASGSVYSPPTRPLPRNTLSRSAFKFKKSSKYCSWKCTALCAVGVSVLLAILLSYFIAMHLFGLNWQLQQTENDTFENGKVNSDTMPTNTVSLPSGDNGKLGGFTQENNTIDSGELDIGRRAIQEIPPGIFWRSQLFIDQPQFLKFNISLQKDALIGVYGRKGLPPSHTQYDFVELLDGSRLIAREQRSLLETERAGRQARSVSLHEAGFIQYLDSGIWHLAFYNDGKNAEQVSFNTIVIESVVECPRNCHGNGECVSGTCHCFPGFLGPDCSRAACPVLCSGNGQYSKGRCLCFSGWKGTECDVPTTQCIDPQCGGRGICIMGSCACNSGYKGESCEEADCIDPGCSNHGVCIHGECHCSPGWGGSNCEILKTMCPDQCSGHGTYLQESGSCTCDPNWTGPDCSNEICSVDCGSHGVCMGGTCRCEEGWTGPACNQRACHPRCAEHGTCKDGKCECSQGWNGEHCTIEGCPGLCNSNGRCTLDQNGWHCVCQPGWRGAGCDVAMETLCTDSKDNEGDGLIDCMDPDCCLQSSCQNQPYCRGLPDPQDIISQSLQSPSQQAAKSFYDRISFLIGSDSTHVIPGESPFNKSLASVIRGQVLTADGTPLIGVNVSFFHYPEYGYTITRQDGMFDLVANGGASLTLVFERSPFLTQYHTVWIPWNVFYVMDTLVMKKEENDIPSCDLSGFVRPNPIIVSSPLSTFFRSSPEDSPIIPETQVLHEETTIPGTDLKLSYLSSRAAGYKSVLKITMTQSIIPFNLMKVHLMVAVVGRLFQKWFPASPNLAYTFIWDKTDAYNQKVYGLSEAVVSVGYEYESCLDLTLWEKRTAILQGYELDASNMGGWTLDKHHVLDVQNGILYKGNGENQFISQQPPVVSSIMGNGRRRSISCPSCNGQADGNKLLAPVALACGIDGSLYVGDFNYVRRIFPSGNVTSVLELSSNPAHRYYLATDPVTGDLYVSDTNTRRIYRPKSLTGAKDLTKNAEVVAGTGEQCLPFDEARCGDGGKAVEATLMSPKGMAVDKNGLIYFVDGTMIRKVDQNGIISTLLGSNDLTSARPLTCDTSMHISQVRLEWPTDLAINPMDNSIYVLDNNVVLQITENRQVRIAAGRPMHCQVPGVEYPVGKHAVQTTLESATAIAVSYSGVLYITETDEKKINRIRQVTTDGEISLVAGIPSECDCKNDANCDCYQSGDGYAKDAKLSAPSSLAASPDGTLYIADLGNIRIRAVSKNKPLLNSMNFYEVASPTDQELYIFDINGTHQYTVSLVTGDYLYNFSYSNDNDITAVTDSNGNTLRIRRDPNRMPVRVVSPDNQVIWLTIGTNGCLKSMTAQGLELVLFTYHGNSGLLATKSDETGWTTFFDYDSEGRLTNVTFPTGVVTNLHGDMDKAITVDIESSSREEDVSITSNLSSIDSFYTMVQDQLRNSYQIGYDGSLRIIYASGLDSHYQTEPHVLAGTANPTVAKRNMTLPGENGQNLVEWRFRKEQAQGKVNVFGRKLRVNGRNLLSVDFDRTTKTEKIYDDHRKFLLRIAYDTSGHPTLWLPSSKLMAVNVTYSSTGQIASIQRGTTSEKVDYDGQGRIVSRVFADGKTWSYTYLEKSMVLLLHSQRQYIFEYDMWDRLSAITMPSVARHTMQTIRSIGYYRNIYNPPESNASIITDYNEEGLLLQTAFLGTSRRVLFKYRRQTRLSEILYDSTRVSFTYDETAGVLKTVNLQSDGFICTIRYRQIGPLIDRQIFRFSEDGMVNARFDYSYDNSFRVTSMQGVINETPLPIDLYQFDDISGKVEQFGKFGVIYYDINQIISTAVMTYTKHFDAHGRIKEIQYEIFRSLMYWITIQYDNMGRVTKREIKIGPFANTTKYAYEYDVDGQLQTVYLNEKIMWRYNYDLNGNLHLLNPSNSARLTPLRYDLRDRITRLGDVQYRLDEDGFLRQRGTEIFEYSSKGLLTRVYSKGSGWTVIYRYDGLGRRVSSKTSLGQHLQFFYADLTYPTRITHVYNHSSSEITSLYYDLQGHLFAMEISSGDEFYIASDNTGTPLAVFSSNGLMLKQIQYTAYGEIYFDSNIDFQLVIGFHGGLYDPLTKLIHFGERDYDILAGRWTTPDIEIWKRIGKDPAPFNLYMFRNNNPASKIHDVKDYITDVNSWLVTFGFHLHNAIPGFPVPKFDLTEPSYELVKSQQWDDIPPIFGVQQQVARQAKAFLSLGKMAEVQVSRRRAGGAQSWLWFATVKSLIGKGVMLAVSQGRVQTNVLNIANEDCIKVAAVLNNAFYLENLHFTIEGKDTHYFIKTTTPESDLGTLRLTSGRKALENGINVTVSQSTTVVNGRTRRFADVEMQFGALALHVRYGMTLDEEKARILEQARQRALARAWAREQQRVRDGEEGARLWTEGEKRQLLSAGKVQGYDGYYVLSVEQYPELADSANNIQFLRQSEIGRR', 'MGLPHRGYSISAGSDADTENEAVMSPEHAMRLWGRGVKSGRSSCLSSRSNSALTLTDTEHENKSDSENEQPASNQGQSTLQPLPPSHKQHSAQHHPSITSLNRNSLTNRRNQSPAPPAALPAELQTTPESVQLQDSWVLGSNVPLESRHFLFKTGTGTTPLFSTATPGYTMASGSVYSPPTRPLPRNTLSRSAFKFKKSSKYCSWKCTALCAVGVSVLLAILLSYFIAMHLFGLNWQLQQTENDTFENGKVNSDTMPTNTVSLPSGDNGKLGGFTQENNTIDSGELDIGRRAIQEIPPGIFWRSQLFIDQPQFLKFNISLQKDALIGVYGRKGLPPSHTQYDFVELLDGSRLIAREQRSLLETERAGRQARSVSLHEAGFIQYLDSGIWHLAFYNDGKNAEQVSFNTIVIESVVECPRNCHGNGECVSGTCHCFPGFLGPDCSRAACPVLCSGNGQYSKGRCLCFSGWKGTECDVPTTQCIDPQCGGRGICIMGSCACNSGYKGESCEEADCIDPGCSNHGVCIHGECHCSPGWGGSNCEILKTMCPDQCSGHGTYLQESGSCTCDPNWTGPDCSNEICSVDCGSHGVCMGGTCRCEEGWTGPACNQRACHPRCAEHGTCKDGKCECSQGWNGEHCTIEGCPGLCNSNGRCTLDQNGWHCVCQPGWRGAGCDVAMETLCTDSKDNEGDGLIDCMDPDCCLQSSCQNQPYCRGLPDPQDIISQSLQSPSQQAAKSFYDRISFLIGSDSTHVIPGESPFNKSLASVIRGQVLTADGTPLIGVNVSFFHYPEYGYTITRQDGMFDLVANGGASLTLVFERSPFLTQYHTVWIPWNVFYVMDTLVMKKEENDIPSCDLSGFVRPNPIIVSSPLSTFFRSSPEDSPIIPETQVLHEETTIPGTDLKLSYLSSRAAGYKSVLKITMTQSIIPFNLMKVHLMVAVVGRLFQKWFPASPNLAYTFIWDKTDAYNQKVYGLSEAVVSVGYEYESCLDLTLWEKRTAILQGYELDASNMGGWTLDKHHVLDVQNGILYKGNGENQFISQQPPVVSSIMGNGRRRSISCPSCNGQADGNKLLAPVALACGIDGSLYVGDFNYVRRIFPSGNVTSVLELRNKDFRHSSNPAHRYYLATDPVTGDLYVSDTNTRRIYRPKSLTGAKDLTKNAEVVAGTGEQCLPFDEARCGDGGKAVEATLMSPKGMAVDKNGLIYFVDGTMIRKVDQNGIISTLLGSNDLTSARPLTCDTSMHISQVRLEWPTDLAINPMDNSIYVLDNNVVLQITENRQVRIAAGRPMHCQVPGVEYPVGKHAVQTTLESATAIAVSYSGVLYITETDEKKINRIRQVTTDGEISLVAGIPSECDCKNDANCDCYQSGDGYAKDAKLSAPSSLAASPDGTLYIADLGNIRIRAVSKNKPLLNSMNFYEVASPTDQELYIFDINGTHQYTVSLVTGDYLYNFSYSNDNDITAVTDSNGNTLRIRRDPNRMPVRVVSPDNQVIWLTIGTNGCLKSMTAQGLELVLFTYHGNSGLLATKSDETGWTTFFDYDSEGRLTNVTFPTGVVTNLHGDMDKAITVDIESSSREEDVSITSNLSSIDSFYTMVQDQLRNSYQIGYDGSLRIIYASGLDSHYQTEPHVLAGTANPTVAKRNMTLPGENGQNLVEWRFRKEQAQGKVNVFGRKLRVNGRNLLSVDFDRTTKTEKIYDDHRKFLLRIAYDTSGHPTLWLPSSKLMAVNVTYSSTGQIASIQRGTTSEKVDYDGQGRIVSRVFADGKTWSYTYLEKSMVLLLHSQRQYIFEYDMWDRLSAITMPSVARHTMQTIRSIGYYRNIYNPPESNASIITDYNEEGLLLQTAFLGTSRRVLFKYRRQTRLSEILYDSTRVSFTYDETAGVLKTVNLQSDGFICTIRYRQIGPLIDRQIFRFSEDGMVNARFDYSYDNSFRVTSMQGVINETPLPIDLYQFDDISGKVEQFGKFGVIYYDINQIISTAVMTYTKHFDAHGRIKEIQYEIFRSLMYWITIQYDNMGRVTKREIKIGPFANTTKYAYEYDVDGQLQTVYLNEKIMWRYNYDLNGNLHLLNPSNSARLTPLRYDLRDRITRLGDVQYRLDEDGFLRQRGTEIFEYSSKGLLTRVYSKGSGWTVIYRYDGLGRRVSSKTSLGQHLQFFYADLTYPTRITHVYNHSSSEITSLYYDLQGHLFAMEISSGDEFYIASDNTGTPLAVFSSNGLMLKQIQYTAYGEIYFDSNIDFQLVIGFHGGLYDPLTKLIHFGERDYDILAGRWTTPDIEIWKRIGKDPAPFNLYMFRNNNPASKIHDVKDYITDVNSWLVTFGFHLHNAIPGFPVPKFDLTEPSYELVKSQQWDDIPPIFGVQQQVARQAKAFLSLGKMAEVQVSRRRAGGAQSWLWFATVKSLIGKGVMLAVSQGRVQTNVLNIANEDCIKVAAVLNNAFYLENLHFTIEGKDTHYFIKTTTPESDLGTLRLTSGRKALENGINVTVSQSTTVVNGRTRRFADVEMQFGALALHVRYGMTLDEEKARILEQARQRALARAWAREQQRVRDGEEGARLWTEGEKRQLLSAGKVQGYDGYYVLSVEQYPELADSANNIQFLRQSEIGRR']
['gene_id "PB.34427"; transcript_id "PB.34427.4";', 'gene_id "PB.34427"; transcript_id "PB.34427.10";', 'gene_id "PB.34427"; transcript_id "PB.34427.13";']

'''

