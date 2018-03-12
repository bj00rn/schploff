from PIL.features import get_supported_modules

print('Pillow was built with following modules: {}'.format(
    repr(get_supported_modules())))
