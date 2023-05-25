import os

import pkg_resources

image_name = os.environ['IMAGE']
version = pkg_resources.get_distribution('pproxy').parsed_version.base_version
tags = ['latest', version]
tags.extend([version[:n] for n in range(len(version)) if version[n] == '.'])
tags = ['{}:{}'.format(image_name, tag) for tag in tags]
print('tags=' + ','.join(tags))
