from flask import Flask, jsonify, request
import requests
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from protobuf_decoder.protobuf_decoder import Parser
from datetime import datetime, timedelta
import json
import threading
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

CREDENTIALS = {
    'ind': [
        {'uid': '3857085341', 'password': '4DF253A2ED267B3B06DF2DF88AF85F3094B62F2D0EB3E10461EB79173D8EC732'},
        {'uid': '3857965664', 'password': '7EABBB7A8EE4B01C2A6A181A6D412DCA018DB0D9CBBFE4D29C50C13CF5F4F26E'},
        {'uid': '3861134746', 'password': '1305B819424EB3E8508F07CAB34D125A78ADE53E368BA59D59C4E82EB227B3E1'},
    ],
    'sg': [
        {'uid': '3230720086', 'password': '0F0B641EEF3F776F2F1680B80A46C8E603A92C7F127037A025A224FA23A4BBD1'},
        {'uid': '3230754615', 'password': 'C1B26515E246D78D2E9CB47B20C2A3CCE344257173E46E3EC6FE85145FF4FA9C'},
        {'uid': '3230720524', 'password': '968C078430FC3BF41A3C88D0DB0FB658B2D12CDEC875D5BCF61B7D59863F9F89'},
        {'uid': '3230818732', 'password': '521751078096CB44D44D706DE2600E952BEB48F31525007016A55C7720B354AF'},
        {'uid': '3230825776', 'password': '9D89323FCCE17EBF5C9A217DD474851E46665C594A665A35CEC691033558FB3A'},
        {'uid': '3230886172', 'password': 'E416DE69AB5CA7EB717154DC7907CE47BF7C38D55463C678E6BD4ADAC1F62DE6'},
        {'uid': '3230887197', 'password': '2606E756FB8CDBA45085406DCA726822DEBFE524470F3E719226306D6F5EF391'},
        {'uid': '3230902631', 'password': 'E14D16569F9FEC51C97EC4D194EA63CC6017953B04E039285876DFEC81709281'},
        {'uid': '3230904757', 'password': '53C663317159A2AF0BBD103A107FBB026FFE1F0A71C90641FCBC4514A9152B6F'},
        {'uid': '3230907324', 'password': '0974CC356BD2A8890090160E562BC7A7A6ACCB42C237384DCEF1D7CFDA47E578'},
        {'uid': '3230903713', 'password': '12A5E87AB51782E499703625B48F2CB891DB4100061E07C2705780C705DBBDF5'},
    {'uid': '3230908317', 'password': 'B686E7F1C803CA344F5F4C3DB3FE21D2D45CDF8892EEF61E03A5941122935D5F'},
    {'uid': '3230904258', 'password': '7889315AF4D9ED29E43290E4677B862B0ABB20601FBD3B00C58A48ECC575FE98'},
    {'uid': '3230903269', 'password': '4B600EFF6D11736053586F279BDC891747262005401A1F15BAD65560B59A58B3'},
    {'uid': '3230909827', 'password': '48649189FA2E72784DDD98DC671650070AA345C49E389299E94541A489822234'},
    {'uid': '3230908817', 'password': 'E07E6F09E3ECE339CEEF306E72109FFC64897CDF33B3FF1B5FE492A5A2BF2B90'},
    {'uid': '3230905780', 'password': '855F2AFA7FC378D23F616F65172B13C51D3D6CD5E444B5E20DBE402A57CC6D36'},
    {'uid': '3230905305', 'password': '4E258DE9970D2C24792FC9B86EEF691C6C22F304F083B2C3EF98FFA173F5306A'},
    {'uid': '3230910360', 'password': 'E734D1A7A27E3ABABD63808E2ACBB19664805ABC9CD18D271E42BBBEBE35623A'},
    {'uid': '3230911406', 'password': '14CD9535ACABDC65E172A6CA92F2FA0811086350530AF34E47ABF1413B1C1647'},
    {'uid': '3230912977', 'password': '1926A58873E08AA7A6618A6C367A5EE2F34F96696A6B30CA224EF96E04EF36B5'},
    {'uid': '3230909366', 'password': '6FD7C160CCF06F1B4C3EABE34FAE772766C029C53FA743A883B0D2DB14306326'},
    {'uid': '3230907845', 'password': 'B7C0E3FDF16AD46E8D0518E20EF5CCE376989F3C93A7184F22673989A9368FB7'},
    {'uid': '3230910934', 'password': '2EAFB1743BA5BC684FB7F5BC01E8384F430D92E3A59800E13FAB6DEA2EF12288'},
    {'uid': '3230915607', 'password': 'FA0E62FB20CF9F36072B48F7755DAF3E3A07DDA78A0B4A1D1FB8C04A8DFAAC91'},
    {'uid': '3230912452', 'password': '0D21772B575B339BABAC31F9476625B0A2E5F50391691859F2B4ED9ED106E573'},
    {'uid': '3230917475', 'password': 'CED8D6CD638A313EA408D47CA1D99FCBA86452FEBBC339EF49191F24A6754D07'},
    {'uid': '3230906826', 'password': '04982081167F54A01EC41D26D2FD8A75E05C3D9666631FDDE4686BE682299A3E'},
    {'uid': '3230914130', 'password': '7AEFBA50E7F3F3DEB9757C6823B9F35367CD72812BC86D3DDD5435BB199C8E5A'},
    {'uid': '3230917980', 'password': 'A0C49616501B90BAA6F9690C2B77BBFDCDD7915CDBA829F95D527F27F5948043'},
    {'uid': '3230915072', 'password': '1C9F0FFE274B8313D9170E324402D166ED694503A8170F849518F191F1A69F1A'},
    {'uid': '3230916958', 'password': '564CA8E828CEF9BC60A97EEFCB03046D3A3AF581513CAB74DA1190DCF86F50BC'},
    {'uid': '3230914592', 'password': '0DEAD683E890F2E1FF180D2D160678BD562AA73366CE7E23E4A7CB913274F9F1'},
    {'uid': '3230918533', 'password': 'AE8E0C19F31FA0591ECD8AC801C486E8932B08BCC98C9AAA586FC98E759535AE'},
    {'uid': '3230919054', 'password': '8A2957237C86860D2117A703508BB4DD1FF28E948F9F856F696418C36D193C93'},
    {'uid': '3230916138', 'password': '3F9DE62CD79782FB5DF05737EE9260754F56001093B4EDDD4B172F3A185B456C'},
    {'uid': '3230920064', 'password': 'FD3D69E8C74132E05EB51F607361EDF5FFFFA4C14C9933F6873E9E4AFDA1CA61'},
    {'uid': '3230921609', 'password': '7AF295C59D93553828E73B1860DA7B3B4B68ABAAB45C62E2843DFFAF41B42159'},
    {'uid': '3230922683', 'password': '8436CE4B02529691CA964BC74812F2D0094A3985BAC9E2ED34FF3710D456A518'},
    {'uid': '3230919547', 'password': '476BA2388D194B3774F0716DB9DF0061742261F17CD995F7A875ECB293448A9B'},
    {'uid': '3230911916', 'password': 'CE3BC9722ED40BE2030FD3818328B0989E14C7F4416822A4B9FABDFF8170D935'},
    {'uid': '3230922129', 'password': 'EEB0AA01BCE43BE09C9EA3076F081F3DA9256CF5455D4275CD2E5A77AF5C85AA'},
    {'uid': '3230923217', 'password': 'B7FEFC6A8C14807D97E3531DE5B9042150899C112C70118CF6FD3CA6400052CA'},
    {'uid': '3230925265', 'password': '6D7B6A4334C08D780ABEF70A63702118E25FFC8BDC155402CA583F63D3EFC9DE'},
    {'uid': '3230926745', 'password': '54B196281143670C9067DEB987A6AF31EF8E7B9F6AEFF3B37215A863CCB11EE9'},
    {'uid': '3230924748', 'password': '1A9BCC257D44833489BA8C3B609470EECAF7D7231E3B29F4177E04C7B4582181'},
    {'uid': '3230923739', 'password': '18453FBA06CB08E61EFA9B44F69E961CC206E0EE59051B3C194D62C6ADF7FED1'},
    {'uid': '3230924237', 'password': 'DA1E9B60AE3036558A1339A1720CD000D27F6CB31495725FA9A3F3FBEA3CA171'},
    {'uid': '3230928917', 'password': '21A22C69EF45C716DEA8DBB046FE65E0311DCE0C0B93403A657ED34618246BCD'},
    {'uid': '3230920573', 'password': 'FD15B18F46AF8AB71F68A83F0C7D84E77751F6F16F52B7F064FF72EE70066AE6'},
    {'uid': '3230929426', 'password': '97954DA77C020CCA9423DB423ADCB0BDEA38A175325918762237D60DAEAD5CA8'},
    {'uid': '3230921162', 'password': '2D7B4EA5F27E7BADE222C668B5911B2A51FFD0A31B44B97E171CAA274C431D0B'},
    {'uid': '3230931208', 'password': '5F6AF35191016532505B1455EC9914270C29E78C7E8A2CD271EAAC168199A731'},
    {'uid': '3230927310', 'password': 'A92299F51A405F4E183442D8695E80F936150690289815BF87F5646ACC841179'},
    {'uid': '3230926228', 'password': '1EC17ED3FC8D239C148549460492DF4B0DD96159F6892DD8C4879B30A38F690F'},
    {'uid': '3230927911', 'password': '243D636D21A981514FA1D6660A6FF33556CEE7170E0E5F192973E4476E3D43E8'},
    {'uid': '3230928390', 'password': '08B0368B43287A1A8F31CCD9AB782E6B47CC5C8FFEE9493C3D6C37D4AB12C389'},
    {'uid': '3230932103', 'password': 'C8980CF21CD09D471DC11BE5EB241D086EA3464338E8102C75C5859E625E63A0'},
    {'uid': '3230929960', 'password': 'E84199343DE04683ECED05C95DEF4C597D3F78A3AA66216387130FF9486F5075'},
    {'uid': '3230930501', 'password': '441AB871A35AD7EF18F3BA1D4C686636547118D3D34758C034A0E93051968052'},
    {'uid': '3230933240', 'password': 'AFBC808B368329C45EA44CB92CF4080D456E03C62BC9E24AF9D66AFAF54BBDBB'},
    {'uid': '3230934847', 'password': 'D607AFEC598F0A1F982CD50EA7C49557194F055971BEE410985BCD7E327D1CA8'},
    {'uid': '3230934314', 'password': '1B3740940C427C2206FBCBABBD4F6906D1CCF4D563C8062AE40666A483CE87A3'},
    {'uid': '3230932680', 'password': '6AA1EA207756BF7F9AE0B211F388624D217C66D28AE10D656AB8CB2A322DAB54'},
    {'uid': '3230939312', 'password': '15D29DD456CC1F6E6E63DF5E887F0197D802340216A67119F9D2D7AE87E5CCF4'},
    {'uid': '3230931577', 'password': '3958CFF354B06D8A9C620440091919334F232922EE860D0724A9B583EC83B835'},
    {'uid': '3230933821', 'password': '5C1F0F34DFAAA40B3F69D3E25142E84CFF130270A5E2F6473B50BC54D888931F'},
    {'uid': '3230940337', 'password': '1E0CA093DFBF371A6121A1923B05895EBBEFD867AE19C8C1CB1593F520B82B62'},
    {'uid': '3230936442', 'password': 'CB2D9FEFE2B43B986319A0972B347768BCABDC47120C5526A6D9379FFD81E1CF'},
    {'uid': '3230925734', 'password': '7852C103D49CB88F891F4BAAB13A4C81C536B45FA5AA0ED2A79370504C5A8A4E'},
    {'uid': '3230940899', 'password': '378C9F29020D8077FA7B6D834A50C15994EA3D819DB8FEF5CC6C04F249DEE19A'},
    {'uid': '3230937644', 'password': '3EF9D950F5B01A51BE465D6E5F4D6073E046CA0A905269C0B1F92E69A081ECC9'},
    {'uid': '3230936945', 'password': '46BDF6D8B369813786B1CF04F3D3A009651D09ACF004F75A3C9D29903CACBA91'},
    {'uid': '3230941341', 'password': '9B8B74E837B52EA2393FE3A69773D38BAB14BCA18269EDD396EBD5CECC82C93F'},
    {'uid': '3230938817', 'password': 'A4A017A2E38905622BDB0B75F50B1614C33E4508B4415A1787D1CCC4984C91AF'},
    {'uid': '3230941854', 'password': 'A8E650631721DC00F9022293ABC2814FF5FF3550B31FABD02A6BAE3A37CB956A'},
    {'uid': '3230944526', 'password': '8E85176A5F191A83DACD723AAF9639E70512F8962CFF6AE39F0F0AD4BF572BE3'},
    {'uid': '3230939840', 'password': 'A9A40D071D433A1F04D5CE0144368DC2EE8C2622C4C3885E2CDE6510172E58E0'},
    {'uid': '3230942917', 'password': '923CBDB8F78A1708238B0A9A151E0C5971160F8A4B67BF44050CC0DD690FD204'},
    {'uid': '3230945044', 'password': '8673B59428F9FF87BCB7B216EA7B40B25EF09643A1E999D0AD7F82D055456587'},
    {'uid': '3230945533', 'password': '7D18B48FB0670FAAE7101578AAE90D381C484AB79358092BC69DC5CB94E87448'},
    {'uid': '3230943951', 'password': 'D5005922F89D93FB3AD9193E44DB597DDF5DD1B827A193F918C4F624C7DD6D3A'},
    {'uid': '3230946070', 'password': '0BEC2704D335781469B46833033581BFE23A96922D2D99F5A545B5D6F640D2B3'},
    {'uid': '3230946592', 'password': '245400DBA49D62F24F3DE83880B241390BE7A167956DF3DBE45AFF1A4A5D5B15'},
    {'uid': '3230942370', 'password': '685D3E235127CFC25E2A190DAE020D24481A0D36D3D3A060003F297306FFDD6C'},
    {'uid': '3230947149', 'password': 'EFF66B7B91F224F1E35674F9E469322CA2B9E50734FE2C62D6C3B7255868EF25'},
    {'uid': '3230948674', 'password': '25F78EF6C596FE4762184A5EE389295FB1595A883AD763FEC1141727763CD3BF'},
    {'uid': '3230943456', 'password': '538C5D2E526CACE7E2D99904CCC6F98392A542665BD7BE97FEDFC1992868F839'},
    {'uid': '3230949209', 'password': '65F2AEC06C2B5CEAAE6C00A264C6CF9AE8FB7B3B4896AFBFEA08724FC647F6D4'},
    {'uid': '3230950275', 'password': '4D24EE68CE48DD00E335D59E46D435F55DECA7B29D7FE62C5006E2023CD0B30F'},
    {'uid': '3230935909', 'password': 'ED8165D3C07F972DE7C09BB1A622100A66592C65AAFD9CAC58AF2279E0A5B758'},
    {'uid': '3230952989', 'password': '4FEE0721C9A4A95CC9DE2BBAA6C71EDE581944D276FFD9196BEF5677D32DBD58'},
    {'uid': '3230950822', 'password': '62AAE4C85CC7C05D8C482C25D96441C1C25BFEA40D66A612961ED9CE7CCCB689'},
    {'uid': '3230951943', 'password': 'AC7C72C1D433D09AAED209FA477584B61AA165448260D4A51810CF26F99C3445'},
    {'uid': '3230948152', 'password': '3F867C70CF97B0344949C325D248A4F983F227F8F6D3DC2A57527D1D4E4901FB'},
    {'uid': '3230953541', 'password': '7FD95A5ECEE4D6A8C92BE0757A1B3E324E57251BE59FFDA46408715A34BE9BA5'},
    {'uid': '3230954048', 'password': 'CF35FF09DEAE03EB45444CEE1CD3624D32170FCCD0367FEBFAA2ECAED6510626'},
    {'uid': '3230949708', 'password': '4A8268070A4554C2522FC5AFE9AC3BCC9A33E718AE5185305D29865840871953'},
    {'uid': '3230935389', 'password': 'D3B69AB1D36801163295CE5EABCE3F96CBCDB4DB4DF0B9848E530E8A84E1877E'},
    {'uid': '3230957315', 'password': '18D2F5D5700F18B42A8460FE331210443E3ADF2CABCF46EAC711C3148F5046DC'},
    {'uid': '3230957855', 'password': 'FF68AF8E58340670655E810D9900CE01B4AE8F281B300877CD584573ACD2C0DA'},
{'uid': '3230956752', 'password': '3A5FD5BCB9BFD4905586CB64C3E96EACBBB594215958BBF41436A201875CC81C'},
{'uid': '3230959061', 'password': '8F311FA843427EC99043E3BB79BD4970EA914CC84A73B66A2B55FDD4B9D2D31F'},
{'uid': '3230958335', 'password': '4B248D1A833F4E1FC66E0ABD48F1E0DD1C0B8803F48A7FB453917737BDD0BF25'},
{'uid': '3230955641', 'password': 'CD3225605DD761F12287DF4F7B4485008A128ADF2F1F3D88B6EE09A49E960526'},
{'uid': '3230955059', 'password': '837583B40A338905ACE14DF68380BD77C86451F71654643EDDE90D9A72896580'},
{'uid': '3230956173', 'password': '44877EE1B7A4FDD11B7A52D27B344F45A66A0483FE2350CF8DDFD12E479C3FFE'},
{'uid': '3230954558', 'password': '5A0ED5B9EE8994AD8C9B294171B3D3FA1B8DCF9BEA2CFA55B0C11DC1EA9B0562'},
{'uid': '3230947625', 'password': '679B01C6CF1CD75842B00898CB5421B83B1B240F9112973FD786BF8A1B601403'},
{'uid': '3230960427', 'password': '09BF0D35ADA89D20B26E58FD1049ED4D2B8914992D8915383964315DFC1AECC4'},
{'uid': '3230952444', 'password': 'E863E6CC0C51893D188095C0AE362792B07A5FAD58C9F125049356693465465F'},
{'uid': '3230964148', 'password': '6F022DE10CD39A901C6F1277477276097E20945187AA84CCA5046CF3445A5BE4'},
{'uid': '3230964686', 'password': 'FDD2609C7270430E9B21FB8AF84C3FD09CB6A6FF03466D47CB96EDF12D08583A'},
{'uid': '3230959458', 'password': '2724B1BEC7D157B55C3AA6D5CFA910416CF91FF424ADBCAA3397CEBDCE75797B'},
{'uid': '3230961022', 'password': '7AC591BBA7CFBA0457AC8E25F584C874ABB33A68209C784D43851305DDB7BAB5'},
{'uid': '3230963117', 'password': '05D3795F3B59AFC57E641C1EFE8A43D7DC558CD7A8A1853B22AFE31AB81CBDD0'},
{'uid': '3230959927', 'password': '26763D00C71320D0CAF2B82A6BF3871F9F65ED1411493DDA1F66EBAE790424EB'},
{'uid': '3230965848', 'password': 'ADE56288E9857084A49B82B35F92CEDBBE8BACE3C58650CC5739CF916578A3C2'},
{'uid': '3230963641', 'password': 'EDE47A83823AC62168D933356980D81E22980B2428A0B46A1F69FC5E0EE7288A'},
{'uid': '3230966870', 'password': '7401FA00FA04942B52C1ABB1B5720ED7E1C91AFAEF50C5C9642BCC8CA87C36ED'},
{'uid': '3230967415', 'password': '871B6DC1D85633C6E0BCE1EFF028BB4F846BB9FF46DC1A0CD01F4A73D8474506'},
{'uid': '3230967947', 'password': 'E9D5A4B16451802530C4488299B2B767ADF3153D456B657B7B53B7D169972A64'},
{'uid': '3230966368', 'password': '9D9AE25C08F7C5BD5D01C5CDA478E3B5E1C3BF05980B8FD51706B1969D22FBBB'},
{'uid': '3230962052', 'password': 'CBF3C16314FE83C5F94AC85355F7BF9BCA5CE388C7561F25F1DC152C194297A3'},
{'uid': '3230968935', 'password': '33B978C3FFE1A8A32B9908BA60DC385F2626DCF95A5E971B68F2967CBD84110B'},
{'uid': '3230961485', 'password': '11735A4C599174B72A8DFD13D331790C4E3E270FB2A71A70F5AAEAFBB6F71043'},
{'uid': '3230970626', 'password': 'AD8E0C541D82DAB791E82085F7FE87A653355D7EE1CBF2C8C49872F8DE777EF7'},
{'uid': '3230969524', 'password': '3ECBCBDDB1DBDC0636BB6609E65C079936C6CF8FABDCEB7FE3BC8E202540D02C'},
{'uid': '3230971158', 'password': '925282B5BE0AF14089AD7F99686935AFA260FEE302402AF54D44BA256E012E48'},
{'uid': '3230938261', 'password': '3ED08EB093EF2E2DCE6C5E153944BF3444E6BE5AAC612B7780B08C90ED033DA8'},
{'uid': '3230962585', 'password': '6A3A89B1D8D7F7672DCE9C39E34F2DE387D6D57F392E68958589B16CAD94CB28'},
{'uid': '3230968447', 'password': 'EE3CF1E2434BCB35D073C5ABCA32DC624D4DC236169921BCAA075A90F6E4A7BA'},
{'uid': '3230971730', 'password': 'F77601C12DE7546E56F63FEB2841360830AD3C9FE3DA9F16B4A2F1904B5CA9C1'},
{'uid': '3230970064', 'password': '91FABB5EC039C58B1C0752D6210EA71A70A1D6A5FE2132FD6B803299BF6CB375'},
{'uid': '3230972289', 'password': '4EB4214A46618C31C47FB45119EA7E38C7A3308A333A40631124BA7AB1DCE884'},
{'uid': '3230975556', 'password': 'B67503410A19505F1E538112D678770269B5420DE18749E62180CF4A6D536D85'},
{'uid': '3230973997', 'password': '8854DF7C612E371D50EDBB38EA1A8ED7B5DA4ED276107E50D5282634D13E6E12'},
{'uid': '3230965247', 'password': '3C56C7BD3BA6A8C20A0FBE3F70D1BA58F33B2BAB61ACD704BFF48E38246FE8ED'},
{'uid': '3230976099', 'password': 'D7C4F80B75B2C1A83D687005A21C075735FE18946B06DCCE456E1A54C3704236'},
{'uid': '3230972856', 'password': '0381753EAE3571CF63426875C68971C1824F2FDD50D75161A90A1BCDBB987DED'},
{'uid': '3230977699', 'password': 'DA525670795F3F56C1E4C62599542962453D5E5FC72F14DBA10BCA1D64174DAB'},
{'uid': '3230978240', 'password': 'AB380C0E759C01DFF421F2188E3B7F8BB5666D7F33F77940EDD01AC03C8C46C9'},
{'uid': '3230977164', 'password': '437FCDF74BB7475A72D8ABF56331604DB3DA76B7A140948EAB7D5E8DB8769A07'},
{'uid': '3230974466', 'password': '9E09A62F32C80334E4237330A92E315FAD596F227812B6E521C5A2EAA830A075'},
{'uid': '3230979972', 'password': 'DF0B5EA6B684493E9FA470E724C3FAEC449297AEEF6F87CC2376F0975C7972B6'},
{'uid': '3230981140', 'password': '702F1D69B352FF05EDFA64F34344349CB23D7F825E05BE3DFBE4CB13CF5840F7'},
{'uid': '3230973408', 'password': '587EF722757A997B2A9D8D1C280F3D07CDFBF947CB90F2F794C9778014F1C489'},
{'uid': '3230981699', 'password': '6D04FA72BF92D6E356F2F7441E8FAA83BFB199C71D81F56437D1B61DCE8D9F2F'},
{'uid': '3230979367', 'password': '3260165E4C006242A42D2C124990816F50509E79CCA033D60E9B31B85FBA913D'},
{'uid': '3230978812', 'password': '0862B6E289FB183D96C480959F140AFB074D02CAE36FF328A7786AAC23F46C5E'},
{'uid': '3230982779', 'password': '220F20FBBB07BFAEC7F60F3EA7A37B84D5F65472E27B7D73950558896E68E999'},
{'uid': '3230985032', 'password': 'F62B9AAB2222D5A9E68A6CF75D095AA6F5EAD550A106C17032C5D1D1FF7C3CBE'},
{'uid': '3230983963', 'password': 'F857E90B45A4EF1590F1FBEC294325552EEE9626A966055E541C81253530BDE0'},
{'uid': '3230982241', 'password': '745506238DB9E58E4C30194820A5237B46DDC9B04FFFA7B9DD350C1AFB0816EB'},
{'uid': '3230985629', 'password': 'B56AA22456607A35A2D2F5F311499A018C5970915CF8C8D0FCA5AA64E52EBE41'},
{'uid': '3230983441', 'password': '42DE6A2A785D30984F9CA093B3FA45834089EE3F99A3B96ED2C459E79202FC0C'},
{'uid': '3230984451', 'password': '7A191E213AFD676A2E3E629959C432BD957BF5C9D9046A0F462AC1D87151F370'},
{'uid': '3230986614', 'password': '23D66A5175F025E69AD41C03ECB9790F1EAE7209761CC9E976E2C6C7D044CE9D'},
{'uid': '3230980549', 'password': 'EEAF34B2B87969D052E1BE79152E0DACD946907DF63B851EFE705569DF7DD55B'},
{'uid': '3230990030', 'password': 'F0AB24F177C71B1E36FCC8FD421107CF7A3E30555EAF9893BBB2538A1B956189'},
{'uid': '3230987279', 'password': 'D3F0BE353D8DF845A45BFE34ADDC6BF272E2C1161FDBB6B543FC3984D3F56E3B'},
{'uid': '3230987757', 'password': 'C763EAB69DCE3935A3DC6D1559253FCF46A643DD2985E359E9C5F76E29C98589'},
{'uid': '3230988390', 'password': '7E28F44E816EED51FFE98F8F20684E7388A25103E94EC028C7B33BD25CF1CE83'},
{'uid': '3230976644', 'password': '5B51F8CC95EEB09C46D78C8E5F10B2CF452E089F4949AA4FD5DEE820DF1936FF'},
{'uid': '3230988954', 'password': 'F45129038F3A85F10836BEC522BA46B903C75B11E19F1458BD3BDEC14F1F3DFE'},
{'uid': '3230990558', 'password': 'BB40F1A7220C3CE56647194F9147900BFAC3880FDC21278B840601B03E8A8E15'},
{'uid': '3230989521', 'password': 'EA8DA41D22178F7009F3EC8CBA812370B5084E915E8F76DBF58463A489C927BE'},
{'uid': '3230993310', 'password': '071CC3BC52FCF0EA9BBC65F048D0F7063926E3249DF877FF305A81957999BA43'},
{'uid': '3230993908', 'password': '127464C5D9EC4BB3ADBC3274B59C49528CA789593C850BF9A3C2A4ADDE5D9346'},
{'uid': '3230996671', 'password': 'C4DA9A733BE2B1A42290ACD91527F9261D94939D831DFBD76EDC58CAB31608E3'},
{'uid': '3230997186', 'password': '9CF4505B652728FF012878B053E49878AB39FE523E1BCEDAF247A357286A7799'},
{'uid': '3230994446', 'password': '3662B2C5EE54C96DA6541F37F6F5CCDA5FC6B2BAE16E448C961E791713033951'},
{'uid': '3230991071', 'password': 'AEBD236A21019E59345F600252D72871EE3757EC9011FCC69910CE97FEDE0C6C'},
{'uid': '3230996216', 'password': '829302AC927C3223AA62B2FC016F4B2E9B6490507CEC9523149B4DF275CA3A5D'},
{'uid': '3230995526', 'password': 'A707A1827F7A4A92176BD212E1CBCE19DE67557B3304C0FDAC39BB3E30C6E622'},
{'uid': '3230992258', 'password': '15600220EE6F6B5FDC1214135037D1E8A9F78FC46E26BCE0A99C56590455673B'},
{'uid': '3230995004', 'password': '4E6B3B5914913AADAB40ABCE3FC9114CF32F7D9ED4B197166CDC94A251E1040C'},
{'uid': '3230992838', 'password': '0EA4686C883527BF77A81F61FA51C795974DA757C0F06243C1EDD82509162B50'},
{'uid': '3231001107', 'password': '9883EA705C1759895B689D2F703A8C25E578132560C881FF73D5D5EC329836F5'},
{'uid': '3230998366', 'password': '826F8DC93A514EF97E5F00A732215F052D2829CDA8E777009997BFDC3AA8A23C'},
{'uid': '3230997745', 'password': '066F103235B55941D4281750971091B3DE52C8EEF9E7B2B8C413FC2FC2C13386'},
{'uid': '3230986205', 'password': '8FC0B53AC23191E5B45A5A3C4ADD052BBF271D57AD3C703F232C551E30063588'},
{'uid': '3230999448', 'password': 'F7B6261DCB049DA4D31F868CC95EEFF38BA2C0809B1F2C6A56CD08F523CF0A2C'},
{'uid': '3230999979', 'password': '7343DB9E1BB1DCF590A03AAAF8785E573EF8CC7C3D0333988DA2ED3E2785C3E9'},
{'uid': '3231003455', 'password': '5ACFC972D222FEF028817105B9AC1B3DD6FAA5642C1A377DEDE955273F1914EA'},
{'uid': '3230991625', 'password': 'A231FEE0E2ACF4A435A44979ECAC59AEE517832EA24B0C6EAA19A30193251409'},
{'uid': '3230998902', 'password': '2A2C917FECE9E9DFC41E3D3BD95E48867CB67E16404219F0EB2582A4A33FEB3C'},
{'uid': '3231005561', 'password': '76BFFCE24C80EDEAF45F0BFFBA6D0E112495BD4D48787F098C90C487573CA71B'},
{'uid': '3231006146', 'password': 'EF1EDFC6EC6E69F620D84E9B3A6020CC9C0A9EBA2241AED2AFFB14B36D8B70BB'},
{'uid': '3231000511', 'password': 'F1EB9703419E8EB05B373C8C0CF1145DD06928A1ACE36AFE048DA27600BFC2CB'},
{'uid': '3231002375', 'password': '670D04D97D4F668A6F6AF56EDBFE51E729D903EFCAF6829D6F86D00D2A064779'},
{'uid': '3231001716', 'password': 'BACCF4DDAF05AABFBB5714FFD1C4EC5F975F96A5D88E9DF1507E23A212AC142E'},
{'uid': '3231004493', 'password': 'E23F008E438EBEB025E0D7A8ED60BAE363A073A7E629671D9912DB650E3696A4'},
{'uid': '3231008432', 'password': 'CAEA291C59B784AC2F5764D0A2C5EE0A42371378BECCBF2190D05341FA4AC895'},
{'uid': '3231008972', 'password': '5225D66FFFA8E765BFCCB117CA60CE29BEE5E7E478D1AB5EDAFB6FFAF354655D'},
{'uid': '3231007299', 'password': 'A0337899C2F9BA17FBFA3B8D29A1F3677041325837C9BE99033EE5B5C5966E2E'},
{'uid': '3231009578', 'password': 'C08A527A2CE6EF097F77C6195654AEB5E371EC28B38A6700259B811B5B7B474F'},
{'uid': '3231007887', 'password': 'B68D7029BC802170C8864651350B97E033979859BA4E283BC65CD9808958AC28'},
{'uid': '3231010725', 'password': '52E857C925089C9FF427969B12B8D2B60437CAFF393DD24520D16C34CE49620D'},
{'uid': '3231005082', 'password': 'AF1E0AFDC94C83EB07A012F9FE609FB4FDB83C4084E2DAC85CFF53B16147875E'},
{'uid': '3231010078', 'password': 'DAA7DE03EBB2E2921DF79CF6C364DC0A6A610B1C2942A1CEABEDC61DF5D7D62D'},
{'uid': '3231003999', 'password': '7BB3E85A5214CFB73C7954AD0036DD01938C30872DAE7E33983BE8FC3CCCC10D'},
{'uid': '3231011211', 'password': '3BCBCE2B7E0335288C9F93BCCF9A765FDE26AD8FE94139EC73309BBA029D887C'},
{'uid': '3231002878', 'password': '160E0B4296FC662C9D8E9F1C0CE1733241B394CBEAB555FB8DA31D39DC49F028'},
{'uid': '3231013456', 'password': '2ECF9202E62D9F1E07BC9DDE8C32BE7380EB02BB9CC4345C998230B3FE83595B'},
{'uid': '3231014567', 'password': '9B8E81E471B1985C4277487DF59BA22F122476D87B1EE98471596A44A3F08084'},
{'uid': '3231011844', 'password': '16CA073DB9766AC222E35C2A55EB5F36AF67235CDE9EF5F855339334A218D28D'},
{'uid': '3231014029', 'password': '79F37904133C1AD52ED425CFE03E628FB4CDA75CB3ED3D4290E51C0F237D1444'},
{'uid': '3231015105', 'password': '6D4044A81705A3DEF00DC5E95A3F4F9DD661F58548C29101A853A0596F93DF47'},
{'uid': '3231015608', 'password': '0A39DB28B12A4DEB5176E700DE68D04E9FB0CA8CA00166B126B065E468EE0785'},
{'uid': '3231016152', 'password': '8AD81FC469728920C8454DCB23345022470774580030A36D7CA74A194229EAE4'},
{'uid': '3231006740', 'password': '8133B583B7F2B0701733C5A0586F28205C3CC8B0DB5004EC731C7BB1EB64FA9F'},
{'uid': '3231018315', 'password': 'C1B0AC574DA747386676FEAC0A15DB6C7DCF1CCE9EFF71AD305C329AAF44ADF9'},
{'uid': '3231016672', 'password': 'FAB40727917046A4C9792FC693690F21C75B48DC2432984960E31DF794B114C9'},
{'uid': '3231017211', 'password': '6C086FE806219551F0E08507C8D4CAF4B6DE22175001B76EBB5BF8FDF0D4ACAA'},
        
    ],
    'br': [
        {'uid': '3864280417', 'password': 'EE565DA510E6A056E7CA89401A76EC196BB95173525ED5E4DB1420E068B5DBAB'},
    ]
}

JWT_GEN_URL = "https://ariflexlabs-jwt-gen.onrender.com/fetch-token"
VALID_KEYS = ["test", "sounava777"]

jwt_cache = {
    'ind': {},
    'sg': {},
    'br': {}
}

def get_jwt(region, uid, password):
    """Fetch or return cached JWT token for a given region and UID."""
    if uid in jwt_cache[region] and datetime.now() < jwt_cache[region][uid]['expiry']:
        return jwt_cache[region][uid]['token']

    try:
        params = {'uid': uid, 'password': password}
        response = requests.get(JWT_GEN_URL, params=params)
        if response.status_code == 200:
            jwt_data = response.json()
            token = jwt_data.get("JWT TOKEN")
            if token:
                jwt_cache[region][uid] = {
                    'token': token,
                    'expiry': datetime.now() + timedelta(hours=1)
                }
                return token
        return None
    except Exception:
        return None

def Encrypt_ID(x):
    x = int(x)
    dec = ['80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '8a', '8b', '8c', '8d', '8e', '8f', '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '9a', '9b', '9c', '9d', '9e', '9f', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'aa', 'ab', 'ac', 'ad', 'ae', 'af', 'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'ba', 'bb', 'bc', 'bd', 'be', 'bf', 'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'ca', 'cb', 'cc', 'cd', 'ce', 'cf', 'd0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9', 'da', 'db', 'dc', 'dd', 'de', 'df', 'e0', 'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9', 'ea', 'eb', 'ec', 'ed', 'ee', 'ef', 'f0', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'fa', 'fb', 'fc', 'fd', 'fe', 'ff']
    xxx = ['1', '01', '02', '03', '04', '05', '06', '07', '08', '09', '0a', '0b', '0c', '0d', '0e', '0f', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '1a', '1b', '1c', '1d', '1e', '1f', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '2a', '2b', '2c', '2d', '2e', '2f', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '3a', '3b', '3c', '3d', '3e', '3f', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '4a', '4b', '4c', '4d', '4e', '4f', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '5a', '5b', '5c', '5d', '5e', '5f', '60', '61', '62', '63', '64', '65', '66', '67', '68', '69', '6a', '6b', '6c', '6d', '6e', '6f', '70', '71', '72', '73', '74', '75', '76', '77', '78', '79', '7a', '7b', '7c', '7d', '7e', '7f']
    x = x / 128
    if x > 128:
        x = x / 128
        if x > 128:
            x = x / 128
            if x > 128:
                x = x / 128
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                m = (n - int(strn)) * 128
                return dec[int(m)] + dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]
            else:
                strx = int(x)
                y = (x - int(strx)) * 128
                stry = str(int(y))
                z = (y - int(stry)) * 128
                strz = str(int(z))
                n = (z - int(strz)) * 128
                strn = str(int(n))
                return dec[int(n)] + dec[int(z)] + dec[int(y)] + xxx[int(x)]

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text, AES.block_size))
    return cipher_text.hex()

def parse_results(parsed_results):
    result_dict = {}
    for result in parsed_results:
        field_data = {}
        field_data['wire_type'] = result.wire_type
        if result.wire_type in ["varint", "string"]:
            field_data['data'] = result.data
        elif result.wire_type == 'length_delimited':
            field_data["data"] = parse_results(result.data.results)
        result_dict[result.field] = field_data
    return result_dict

def get_available_room(input_text):
    parsed_results = Parser().parse(input_text)
    parsed_results_dict = parse_results(parsed_results)
    return json.dumps(parsed_results_dict)

def fetch_player_data(token, endpoint, host, player_id):
    """Helper function to fetch player data with a given token."""
    try:
        data = bytes.fromhex(encrypt_api(f"08{Encrypt_ID(player_id)}1007"))
        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB48',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'Authorization': f'Bearer {token}',
            'Content-Length': '16',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': host,
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        response = requests.post(endpoint, headers=headers, data=data, verify=False)
        if response.status_code == 200:
            hex_response = binascii.hexlify(response.content).decode('utf-8')
            json_result = get_available_room(hex_response)
            return json.loads(json_result), True
        return None, False
    except Exception:
        return None, False

def get_player_info(region, endpoint, host):
    def inner():
        try:
            player_id = request.args.get('uid')
            if not player_id:
                return jsonify({
                    "status": "error",
                    "message": "Player ID is required",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }), 400

            api_key = request.args.get('key')
            if not api_key or api_key not in VALID_KEYS:
                return jsonify({
                    "status": "error",
                    "message": "Invalid or missing API key",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }), 401

            tokens = []
            with ThreadPoolExecutor(max_workers=len(CREDENTIALS[region])) as executor:
                futures = [
                    executor.submit(get_jwt, region, cred['uid'], cred['password'])
                    for cred in CREDENTIALS[region]
                ]
                for future in futures:
                    token = future.result()
                    if token:
                        tokens.append(token)

            if not tokens:
                return jsonify({
                    "status": "error",
                    "message": "Failed to retrieve any JWT tokens",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }), 500

            first_result = None
            with ThreadPoolExecutor(max_workers=len(tokens)) as executor:
                futures = [
                    executor.submit(fetch_player_data, token, endpoint, host, player_id)
                    for token in tokens
                ]
                for future in futures:
                    result, success = future.result()
                    if success and first_result is None:
                        first_result = result

            if first_result is not None:
                return first_result

            return jsonify({
                "status": "error",
                "message": "All API requests failed",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }), 500

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }), 500
    return inner

app.route('/api/data/ind', methods=['GET'], endpoint='get_player_info_ind')(
    get_player_info('ind', 'https://client.ind.freefiremobile.com/LikeProfile', 'clientbp.ggblueshark.com')
)
app.route('/api/data/sg', methods=['GET'], endpoint='get_player_info_sg')(
    get_player_info('sg', 'https://clientbp.ggblueshark.com/LikeProfile', 'clientbp.ggblueshark.com')
)
app.route('/api/data/br', methods=['GET'], endpoint='get_player_info_br')(
    get_player_info('br', 'https://client.us.freefiremobile.com/LikeProfile', 'client.us.freefiremobile.com')
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)