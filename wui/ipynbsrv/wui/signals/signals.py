from django.dispatch import Signal


example_signal = Signal(providing_args=['arg1', 'arg2'])
