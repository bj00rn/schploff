from PIL.features import get_supported_modules

print('Pillow was built with follwing modules: {}'.format(repr(get_supported_modules())))
