from PIL import features

print('Pillow was built with following modules: {}'.format(
    repr(features.get_supported())))
