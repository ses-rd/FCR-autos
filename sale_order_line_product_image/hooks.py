import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    _logger.info("No external WebP decoder is required; the module will use Pillow when available.")
