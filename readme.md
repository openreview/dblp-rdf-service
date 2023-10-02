# DBLP query server

# Setup
## Apache Jena

# Goal
Given an author ID
> <https://dblp.org/pid/m/AndrewMcCallum>

Construct author info with publications as an XML record, e.g.,

```

<dblpperson name="Andrew McCallum" pid="m/AndrewMcCallum" n="408">
  <person key="homepages/m/AndrewMcCallum" mdate="2022-11-02">
    <author pid="m/AndrewMcCallum">Andrew McCallum</author>
    <note type="affiliation">University of Massachusetts Amherst, USA</note>
    <url>http://www.cs.umass.edu/~mccallum/</url>
    <url>https://scholar.google.com/citations?user=yILa1y0AAAAJ</url>
    <url>https://dl.acm.org/profile/81100553872</url>
    <url>https://dl.acm.org/profile/99659165411</url>
    <url>https://zbmath.org/authors/?q=ai:mccallum.andrew-kachites</url>
    <url>https://mathgenealogy.org/id.php?id=110723</url>
    <url>https://en.wikipedia.org/wiki/Andrew_McCallum</url>
    <url>https://twitter.com/andrewmccallum</url>
    <url>https://www.wikidata.org/entity/Q4757923</url>
    <url>https://mathscinet.ams.org/mathscinet/MRAuthorID/798077</url>
  </person>
  <r>
    <inproceedings key="conf/acl/ChangSRM23" mdate="2023-08-10">
      <author pid="130/1022">Haw-Shiuan Chang</author>
      <author pid="301/6251">Ruei-Yao Sun</author>
      <author pid="331/1034">Kathryn Ricci</author>
      <author pid="m/AndrewMcCallum">Andrew McCallum</author>
      <title>Multi-CLS BERT: An Efficient Alternative to Traditional Ensembling.</title>
      <pages>821-854</pages>
      <year>2023</year>
      <booktitle>ACL (1)</booktitle>
      <ee type="oa">https://doi.org/10.18653/v1/2023.acl-long.48</ee>
      <ee type="oa">https://aclanthology.org/2023.acl-long.48</ee>
      <crossref>conf/acl/2023-1</crossref>
      <url>db/conf/acl/acl2023-1.html#ChangSRM23</url>
    </inproceedings>
  </r>
  ...
</dblpperson>

```


# Issues
- Server is throwing OOM errors
