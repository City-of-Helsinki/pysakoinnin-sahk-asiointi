# Changelog

## [3.0.0](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.6.1...pysakoinnin-sahk-asiointi-v3.0.0) (2026-02-15)


### ⚠ BREAKING CHANGES

* remove obsolete AuditLog model

### Features

* Remove obsolete AuditLog model ([deacd7e](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/deacd7efc3bcd5b6d4ec65fd16adb47a3f2d4f3d))

## [2.6.1](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.6.0...pysakoinnin-sahk-asiointi-v2.6.1) (2026-02-11)


### Dependencies

* Bump cryptography from 46.0.3 to 46.0.5 ([ba42ff5](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/ba42ff5c7fef56efcd5e62391ff52e13004fb25c))

## [2.6.0](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.5.3...pysakoinnin-sahk-asiointi-v2.6.0) (2026-02-09)


### Features

* Add json application logging to gunicorn ([595bc9f](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/595bc9fa63c5facd52e81705050bdaf9f8b30f47))
* Allow dynamic sentry trace ignore paths ([b51b0fc](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/b51b0fc0e2442d278b6a150ad2a67f6db792fa87))
* Change audit log to use resilient logger ([9235906](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/9235906ef7a8a9e6f6d5879fc6c0d85d4fb53558))


### Bug Fixes

* Change audit log environment variable audit_log_env ([297734d](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/297734df3da615d8494cef993b54fcd7c986bfdb))
* Refactor pipelines ([#239](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/issues/239)) ([b64bd72](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/b64bd72ed7e771e5908e33d84df654e5f5213db2))


### Dependencies

* Add django logger extra ([4f88763](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/4f88763846f4bb3e82f03f43b2b9ecf0160994f2))
* Add resilient logger dependency ([297bc1d](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/297bc1da6b6acf6e644ec386726556be9b4ef1e4))
* Bump django from 5.2.9 to 5.2.11 ([887bad4](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/887bad44f253fa1f27757fd591b807ddfb0c38c0))
* Bump pip from 25.3 to 26.0 ([fe52d6a](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/fe52d6ad9cfcea5ba4feadc0687644e94f160785))
* Bump pyasn1 from 0.6.1 to 0.6.2 ([f9a94e2](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/f9a94e2e3bdb60a73c80fdf76dc115c32c67808b))
* Bump wheel from 0.45.1 to 0.46.2 ([42223f8](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/42223f81f4e3adfe3029fad08b6257c4eb0bbd24))

## [2.5.3](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.5.2...pysakoinnin-sahk-asiointi-v2.5.3) (2025-12-04)


### Dependencies

* Bump django from 5.2.8 to 5.2.9 ([1fe2051](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/1fe20515ad0f3bc003f6392a16c0fbc90ee54ded))

## [2.5.2](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.5.1...pysakoinnin-sahk-asiointi-v2.5.2) (2025-11-27)


### Dependencies

* Bump django from 5.2.7 to 5.2.8 ([d7bbf32](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/d7bbf32fbc929cc5fa24199170080c78b57f13a2))

## [2.5.1](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.5.0...pysakoinnin-sahk-asiointi-v2.5.1) (2025-11-03)


### Bug Fixes

* Remove dueDate from FoulRequestMetadata ([9b925f3](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/9b925f3dbd9b87503c4fb99da7bafeaa095e3a56))


### Dependencies

* Bump pip from 25.2 to 25.3 ([e1260be](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/e1260be09f8feaeb0b2f042b8de312dbd6e66807))

## [2.5.0](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.4.0...pysakoinnin-sahk-asiointi-v2.5.0) (2025-10-24)


### Features

* **sentry:** Update sentry configuration ([3cc636d](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/3cc636d53d97cebb32c108abc77d802cad4a7de8))


### Bug Fixes

* Disable mailer lockfile ([114eea8](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/114eea8cf2072e8779d8eb919dd6b206494355e3))


### Dependencies

* Bump sentry-sdk from 2.39.0 to 2.42.0 ([a19127e](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/a19127ebe6ee1246bb4d5e8b0bdc071d057cb76e))

## [2.4.0](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.3.0...pysakoinnin-sahk-asiointi-v2.4.0) (2025-10-16)


### Features

* Add CSP ([41d657a](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/41d657ab9400526ccba35a845c1352812d94d818))
* Add retry_deferred_low management command ([c72a086](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/c72a0866de708f3552ba733cdc0caf7a277f305e))
* Expect Objection.email to be an email ([f7c8280](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/f7c8280cd7f1f6a7e8f7dcb97877908c9688ea3a))
* ExtendDueDate.metadata has required fields ([50dcd15](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/50dcd15670ebd46293759cde3375b9c407462340))


### Bug Fixes

* Check attachment existense before iterating them ([fcf4258](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/fcf4258587bac14a8b0c981a25fc3842508988dc))
* Define return values for optional fields ([72baa3b](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/72baa3b570f2249839b3c14b8a336e043c69faa3))
* Properly raise errors for setDocumentStatus endpoint ([d38efc7](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/d38efc7d6325ebb4350b11e95798ed8f6accfdbd))
* Readiness and health endpoints ([ff507dd](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/ff507ddbb70ee6305d4c984771a1252f81870c1e))
* Resolve build error when installing python modules ([69738e1](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/69738e18b76b3caccd125aa1e96e6bb40deea4ba))
* Support CORS_ALLOWED_ORIGIN_REGEXES ([4d5f019](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/4d5f019c8a68d26fa92845584169381c1c1f8350))
* Use logger in sentry_scrubber ([1f50cf9](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/1f50cf98e90d5381b9df8065e9116b3f7be8f824))


### Dependencies

* Add email-validator as a requirement ([15f5795](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/15f5795f8ae3e79dd3cad08a315010bb9a811a58))
* Add ipython and pip-tools, remove ruff ([fc1f2ce](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/fc1f2ce7031d259f5586c2a4801c612da7e2dbe3))
* Add syrupy to dev requirements ([7add9fc](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/7add9fcc8bb0d70d271b5402513b793d79d88696))
* Upgrade to django 5.2 ([81e4c6f](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/81e4c6f9b8a97fe86df74b573f00f126815bd90e))

## [2.3.0](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.2.1...pysakoinnin-sahk-asiointi-v2.3.0) (2025-09-12)


### Features

* Use default email address in outgoing mails ([5febf39](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/5febf394eb8e77bc0bbbf377926c5193340dc649))

## [2.2.1](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.2.0...pysakoinnin-sahk-asiointi-v2.2.1) (2025-09-10)


### Dependencies

* Bump django from 4.2.23 to 4.2.24 ([4e7bc6b](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/4e7bc6b75419fc80045291188d1dda5839af9cb2))
* Use psycopg-c ([2c6d304](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/2c6d304a870ebb5406361a000c3b34edb3323b4a))

## [2.2.0](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.1.1...pysakoinnin-sahk-asiointi-v2.2.0) (2025-09-01)


### Features

* Change default email address ([d7f30ab](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/d7f30abc528021345b5523d82994a42dc0360e8a))

## [2.1.1](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.1.0...pysakoinnin-sahk-asiointi-v2.1.1) (2025-09-01)


### Dependencies

* Upgrade to python 3.12 ([9f070f3](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/9f070f3890cdda597bc6f99b3a76359733e1fcbd))

## [2.1.0](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v2.0.0...pysakoinnin-sahk-asiointi-v2.1.0) (2025-07-03)


### Features

* Allow OUTGOING_REQUEST_TIMEOUT read from env ([22d7084](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/22d7084fed5bc5cc7d6177645cc0328dc5c76e77))


### Bug Fixes

* Increase outgoing request timeout ([3c9c47b](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/3c9c47bfececf8db568048257c3ca628a34704a6))

## [2.0.0](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v1.1.6...pysakoinnin-sahk-asiointi-v2.0.0) (2025-06-25)


### ⚠ BREAKING CHANGES

* remove getDocumentByTransactionId endpoint

### Features

* Improve Gunicorn settings ([08eec4c](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/08eec4ca980768e60b0913bed7a8c74593d23eac))


### Bug Fixes

* Remove getDocumentByTransactionId endpoint ([bafce9a](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/bafce9a45dbcb28c17c277c0671e9cfd0a3bc835))

## [1.1.6](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v1.1.5...pysakoinnin-sahk-asiointi-v1.1.6) (2025-06-11)


### Dependencies

* Bump django 4.2.22 -&gt; 4.2.23, requests 2.32.3 -> 2.32.4 ([f274641](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/f274641a52b0bc77ed0fc7f394de30b53fda31f3))

## [1.1.5](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v1.1.4...pysakoinnin-sahk-asiointi-v1.1.5) (2025-06-10)


### Dependencies

* Bump django from 4.2.21 to 4.2.22 ([e5c23ba](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/e5c23baa5d34cb8633341f66d7b5b85c0c91574c))

## [1.1.4](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v1.1.3...pysakoinnin-sahk-asiointi-v1.1.4) (2025-05-13)


### Dependencies

* Bump django from 4.2.20 to 4.2.21 ([7954f54](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/7954f540be39d059130eec4feb3975849d8bbb98))

## [1.1.3](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v1.1.2...pysakoinnin-sahk-asiointi-v1.1.3) (2025-04-24)


### Dependencies

* Bump gunicorn from 22.0.0 to 23.0.0 ([7d76e55](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/7d76e55cef04c58815e06e0556ae9d6e09b6dd1e))

## [1.1.2](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v1.1.1...pysakoinnin-sahk-asiointi-v1.1.2) (2025-03-07)


### Bug Fixes

* Constant condition in _get_operation_name ([f3707a7](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/f3707a7eae0753579f7eac3b57ddb2ad68b8b992))


### Dependencies

* Bump cryptography from 43.0.1 to 44.0.1 ([2eb33f0](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/2eb33f0e8d8a0e95d15bb61fcb406b39302833d0))
* Bump django from 4.2.17 to 4.2.20 ([fd1f869](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/fd1f8699f6cc6d3e3857f97e8cf98fdf497d38d9))
* Bump python-jose from 3.3.0 to 3.4.0 ([bccf71e](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/bccf71e73b4d0382efd4d0ec42dc5e0236027d25))

## [1.1.1](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v1.1.0...pysakoinnin-sahk-asiointi-v1.1.1) (2024-12-17)


### Bug Fixes

* Add 'httplib_request_kw' to sentry scrublist ([f0bf81f](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/f0bf81fa85ffe5cc20980038b85857627719677c))
* Make GDPR api more compliant with standard ([8cf6957](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/8cf69573cb00dcb6d51b5df11b7dd26748eb0fc3))
* Sentry scrub recursively and deny "request" and "body" ([124a7ea](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/124a7ea96a8dcdaec4693e422a649aa1f134300c))
* Support lists in token auth settings ([149adf2](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/149adf20f3160b98c70ad13b503ef8c28559c2f3))


### Dependencies

* Bump django from 4.2.16 to 4.2.17 ([029bebf](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/029bebfa8d40f3118ecabfbaa08029ed29b5d0aa))

## [1.1.0](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v1.0.4...pysakoinnin-sahk-asiointi-v1.1.0) (2024-10-08)


### Features

* Add django-heluser's back-channel logout ([62b7004](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/62b7004166b57b363f897794a976f8e43b9ee13c))
* Add timeout to all requests ([c6541b8](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/c6541b84098cad98f07d7862708cefccfa47f16d))
* Add timeout to virus scanning request ([2c2d044](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/2c2d044fe20e2b5c46f745535eeef93975c3e2b1))
* **settings:** Use DATABASE_PASSWORD if present in env ([401128b](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/401128bb126580072972d3668366def2c3b13627))
* Strip api parameter values ([88154c5](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/88154c5cbc141668e63663dee7e88bf3f71d888d))


### Dependencies

* Bump requirements with security fixes ([15f4e88](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/15f4e888266381ab8425df525c0276bbfda084f3))
* Bump urllib3 from 2.2.1 to 2.2.2 ([b82346b](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/b82346b68e86667cc9258f0e636ff1da19ba4338))

## [1.0.4](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v1.0.3...pysakoinnin-sahk-asiointi-v1.0.4) (2024-06-19)


### Bug Fixes

* Downgrade django-ninja to v0.x ([3509812](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/3509812568f7ee27f85ce29539e24bd349e88341))


### Dependencies

* Upgrade requests to v2.32.3 ([0b27853](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/0b278538a7e17869f80912d9c34e932acef7a057))

## [1.0.3](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v1.0.2...pysakoinnin-sahk-asiointi-v1.0.3) (2024-06-13)


### Dependencies

* Upgrade dependencies ([dd21336](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/dd213360af1c36dad9ed83c12eb5629dc2bc8953))
* Upgrade Django and other dependencies ([576f423](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/576f423b58bcf7520ce975b478f85a62811b55f1))

## [1.0.2](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/compare/pysakoinnin-sahk-asiointi-v1.0.1...pysakoinnin-sahk-asiointi-v1.0.2) (2024-04-10)


### Bug Fixes

* Add missing commas to sentry deny list ([8e27dcc](https://github.com/City-of-Helsinki/pysakoinnin-sahk-asiointi/commit/8e27dccda6e3651f3c576bea6ecf36e3d0482c4c))
