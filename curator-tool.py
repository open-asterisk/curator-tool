# Open Asterisk Curator Tool
import classifier.classifier as classifier
import backend
import argparse

BANNER = """
                                                  |-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|
                    ▓▓▓▓▓▓▓▓▓▓                    |   ___                                 |
                   ▓██████████▓                   |  / _ \ _ __   ___ _ __                |
                   ▓██████████▓                   | | | | | '_ \ / _ \ '_ \   _____       |
                   ▓██████████▓                   | | |_| | |_) |  __/ | | | |_____|      |
                   ▓██████████▓                   |  \___/| .__/ \___|_| |_|  _     _     |
                    ▓████████▓                    |    / \|_|___| |_ ___ _ __(_)___| | __ |
    ▓██▓▓▓▓▓        ▓████████▓        ▓▓▓▓▓██▓    |   / _ \ / __| __/ _ \ '__| / __| |/ / |
   ▓█████████▓▓▓▓   ▓████████▓    ▓▓▓▓████████▓   |  / ___ \\__ \ ||  __/ |  | \__ \   <  |
  ▓██████████████▓▓▓▓████████▓▓▓▓▓█████████████▓  | /_/   \_\___/\__\___|_|  |_|___/_|\_\ |
  ▓████████████████████████████████████████████▓  |                                       |
   ▓▓▓▓████████████████████████████████████▓▓▓▓   |-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|
       ▓▓▓▓▓▓▓▓▓▓▓██████████████▓▓▓▓▓▓▓▓▓▓        |                                       |
                 ▓██████████████▓                 | curator-tool                          |
                ▓████████████████▓▓               |                                       |
              ▓▓███████▓▓▓▓████████▓▓             | use python curator-tool.py -h to      |
            ▓▓████████▓    ▓█████████▓▓           | display the help page                 |
         ▓▓██████████▓      ▓██████████▓▓         |                                       |
        ▓██████████▓          ▓██████████▓        |                                       |
        ▓█████████▓            ▓█████████▓        |                                       |
         ▓████▓▓▓▓              ▓████▓▓▓▓         | https://github.com/open-asterisk      |
          ▓▓▓▓                   ▓▓▓▓             |                                       |
                                                  |-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-|
"""

parser = argparse.ArgumentParser(description='Open Asterisk Curator Tool')
subparsers = parser.add_subparsers(dest='command')

importer_parser = subparsers.add_parser('import')
importer_parser.add_argument('-idir', '--import_directory', required=True, help='The directory to import')
importer_parser.add_argument('-odir', '--output_directory', required=True, help='The directory to output to')
importer_parser.add_argument('-r', '--recursive', action='store_true', help='Import recursively?')

classifier_parser = subparsers.add_parser('classify')
classifier_parser.add_argument('-db', '--database', required=True, help='The path to the database')
classifier_parser.add_argument('-m', '--method', required=True, choices=['exts', 'ml', 'mixed'], help='The classification method to use')
classifier_parser.add_argument('-si', '--show_info', action='store_true', help='Display database information')
classifier_parser.add_argument('-cm', '--classifier_model', help='The path to the ML classifier model to use')
classifier_parser.add_argument('-ex', '--external_plugin_db', help='External plugin database to use instead of the internal one')

args = parser.parse_args()

if args.command == 'import':
    backend_import = backend.BackendImporter(args.import_directory, args.output_directory, args.recursive)
    print(BANNER)
    backend_import.commence_import()

if args.command == 'classify':
    classifier = classifier.FileClassifier(args.database, args.method, args.show_info, args.classifier_model, args.external_plugin_db)
    print(BANNER)
    classifier.begin_classifier()
    