import json
import os

import pkg_resources

image_name = os.getenv('IMAGE')
version = pkg_resources.get_distribution('pproxy').parsed_version.base_version
tags = ['latest', version]
tags.extend([version[:n] for n in range(len(version)) if version[n] == '.'])
print("tags=" + json.dumps([image_name + tag for tag in tags]))
