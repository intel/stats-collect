module.exports = {
    env: {
        browser: true,
        es2022: true,
        commonjs: true
    },
    extends: [
        'standard',
        'eslint:recommended',
        'plugin:wc/recommended',
        'plugin:lit/recommended'
    ],
    parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module'
    },
    rules: {
        // 'ignoredNodes: ['TemplateLiteral > *'] is used to stop ESLint complaining about
        // indentation in lit html templates.
        indent: ['error', 4, { ignoredNodes: ['TemplateLiteral *'] }]
    },
    settings: {
        wc: {
            elementBaseClasses: ['LitElement']
        }
    }
}
