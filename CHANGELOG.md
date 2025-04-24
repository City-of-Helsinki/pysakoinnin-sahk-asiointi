# Changelog

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
