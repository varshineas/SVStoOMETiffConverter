# SVS to OME-TIFF Converter

A Python tool that converts `.svs` files into `.ome.tiff` format using the BioFormats2Raw and Raw2OmeTiff CLI tools from OME.

---

## Requirements

- Python 3.7+
- Java 11+ (check with `java -version`)
- [bioformats2raw](https://github.com/glencoesoftware/bioformats2raw/releases) CLI installed and in your PATH
- [raw2ometiff](https://github.com/glencoesoftware/raw2ometiff/releases) CLI installed and in your PATH

---

## Usage

1. Clone this repository:

```bash
git clone https://github.com/YOUR_USERNAME/svs-ome-converter.git
cd svs-ome-converter

python svsToOmetiffConversion.py /path/to/your/svs_files

