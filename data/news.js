// Lab news, edited by hand. Newest first is not required; the page sorts by date.
// date is "YYYY-MM" or "YYYY-MM-DD". text may contain HTML (links, <i>species</i>);
// write "&" in text as "&amp;". text is optional.
// New papers and preprints since 2022 are added to the News page automatically
// from data/publications.js, so they do not need an entry here.
// image (optional): { src, alt }; a missing file is skipped silently.
window.NEWS = [
  {
    date: "2026-09",
    title: "Fantastic visit and talk from Dr. Polly Hsu, Michigan State University, on the Translational Landscape in Plants!",
    text: "Thank you to the TAMU Interdisciplinary Graduate Program in Genetics &amp; Genomics (GGEN), Amanda Joseph and Elliott Runyan for hosting the seminar and coordinating the visit."
  },
  {
    date: "2026-06",
    title: "Congratulations to Adekola for being awarded the Tom Slick Graduate Research Fellowship!"
  },
  {
    date: "2026-04",
    title: "Congratulations Catherine Chaison, 1st place Undergraduate Oral Presentation award, and Sierra Sanders, 3rd place Graduate Oral Presentation award at the 2026 Ecological Integration Symposium!",
    image: { src: "assets/img/news/ies2026_awards.jpg", alt: "Lab members at the 2026 Ecological Integration Symposium" }
  },
  {
    date: "2025-09",
    title: "Congratulations to Matt for receiving the 2025 EEB Graduate Teaching Award!"
  },
  {
    date: "2024-09",
    title: "Welcome Matthew!",
    image: { src: "assets/img/people/marano.jpg", photo: true, alt: "Matthew Marano" },
    text: "We are excited to have Matthew Marano joining our lab as a Ph.D. student in the Interdisciplinary Doctoral Degree Program in Ecology and Evolutionary Biology (EEB) to work on the population genetics of de novo genes in mammals."
  },
  {
    date: "2023-11",
    title: "SMBE satellite meeting on De Novo Gene Birth at Texas A&M",
    text: "The lab co-organized a Society for Molecular Biology and Evolution satellite meeting on de novo gene birth, held at Texas A&amp;M in November 2023."
  },
  {
    date: "2023-08",
    title: "Welcome to the lab Sierra!",
    image: { src: "assets/img/people/sanders.jpg", photo: true, alt: "Sierra Sanders" },
    text: "Great to have Sierra Sanders as a Ph.D. student in the Interdisciplinary Doctoral Degree Program in Ecology and Evolutionary Biology (EEB) joining us to study how de novo genes evolve and become functional in plants. Congrats Sierra for being awarded a three-year EEB Fellowship!"
  },
  {
    date: "2022-12-05",
    title: "Welcome Adekola!",
    image: { src: "assets/img/people/owoyemi.jpg", photo: true, alt: "Adekola Owoyemi" },
    text: "I am very excited to welcome Adekola Owoyemi to the lab as a Ph.D. student in Ecology and Conservation Biology. Adekola is interested in integrating computational biology, genomics and phylogenetics to identify and characterize de novo genes in plants. Adekola is the recipient of a three-year ECCB Graduate Fellowship: congratulations!"
  }
];

// One figure per paper on the News page, keyed by DOI. Files live in
// assets/img/news/; a missing file is skipped. The credit line is built
// from the publication record plus label and license here.
window.NEWS_FIGURES = {
  "10.64898/2026.10.13.758884": { file: "owoyemi2026_fig1.png", label: "Fig. 1" },
  "10.1093/nar/gkag234": { file: "chothani2026_graphical_abstract.jpg", label: "Graphical abstract", license: "CC BY" },
  "10.1093/gbe/evag009": { file: "casola2026_fig1.jpg", label: "Fig. 1", license: "CC BY" },
  "10.1098/rsos.240755": { file: "copeland2024_fig4.jpg", label: "Fig. 4", license: "CC BY" },
  "10.1002/bies.202400146": { file: "pereira2025_fig2.jpg", label: "Fig. 2", license: "CC BY-NC" },
  "10.1186/s13100-022-00282-2": { file: "markova2022_fig6.jpg", label: "Fig. 6", license: "CC BY" },
  "10.7717/peerj.12791": { file: "casola2022_peerj_fig2.jpg", label: "Fig. 2", license: "CC BY" }
};
