<?php
/**
 * Expose Rank Math SEO meta fields to the WordPress REST API so pub-tools
 * (the `claude` Editor user) can read/write them via /wp/v2/posts.
 *
 * Rank Math does NOT expose these fields via REST by default -- see
 * integrations/wordpress/SITE_INVENTORY.md. Tracked by Linear PUB-6.
 *
 * IMPORTANT: this file is NOT executed from this repo. It is the canonical
 * source of the snippet so it is never lost again. To activate it, paste the
 * snippet below into the Blackbird child theme's functions.php (Appearance ->
 * Theme File Editor, or via SFTP/WPEngine). WordPress theme files are not
 * editable through the REST API, so this is a manual step on Jamie's side.
 *
 * After it's live, ping Rookwood to test + roll out (see PUB-6 plan).
 */

add_action( 'init', function () {
    $fields = [
        'rank_math_title',
        'rank_math_description',
        'rank_math_focus_keyword',
        'rank_math_canonical_url',
    ];
    foreach ( $fields as $field ) {
        register_post_meta( 'post', $field, [
            'show_in_rest'  => true,
            'single'        => true,
            'type'          => 'string',
            'auth_callback' => function () {
                return current_user_can( 'edit_posts' );
            },
        ] );
    }
} );
