            if not records.check_signature_passes():
                print_red('WARNING: Digests do not match')
                print_red('It may be a security issue to continue')
                _continue: str = input('Continue? (y/N)').lower()
                if _continue == '' or _continue == 'n' or not _continue == 'y':
                    print_gray('Aborting...')
                    sys.exit(-1)
                else:
                    print_red('WARNING: Loading data file anyway. Fingers crossed.')
            else:
                print_grey('Digests matched OK.')
				