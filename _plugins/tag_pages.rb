# Auto-generate one /tags/<slug>/ page per unique topic tag at build time.
#
# A tag is "topic" (and gets a page generated) if it's used in any article's
# `categories` field AND it's not:
#   - the slug of a section page (pages with `navGroup: section` in front matter)
#   - one of the generic flags ("articles", "index")
#
# New article tagged with a never-before-seen slug → next build emits a new page.
# No manual list to maintain.

module Jekyll
  class TagPage < Page
    def initialize(site, base, tag, overrides = {})
      @site = site
      @base = base
      @dir  = File.join('tags', tag)
      @name = 'index.html'

      process(@name)
      read_yaml(File.join(base, '_layouts'), 'tag.html')

      data['tag']   = tag
      data['title'] = TagPage.display_name(tag, overrides)
    end

    # Look up a display name in `_data/tag_overrides.yml` (case-insensitive on
    # the slug). Falls back to the slug with hyphens → spaces and each word
    # title-cased.
    def self.display_name(tag, overrides)
      key = tag.to_s.downcase
      if overrides.is_a?(Hash) && overrides[key]
        overrides[key].to_s
      else
        key.tr('-', ' ').split(' ').map(&:capitalize).join(' ')
      end
    end
  end

  class TagGenerator < Generator
    safe true
    priority :low

    GENERIC = %w[articles index].freeze

    def generate(site)
      # When `pages` is a declared collection, the section pages live there.
      # `site.pages` in Ruby code refers to static top-level pages only.
      pages_coll = site.collections['pages']
      section_slugs = if pages_coll
        pages_coll.docs
          .select { |p| p.data['navGroup'] == 'section' }
          .map    { |p| p.data['content-category'] }
          .compact
      else
        []
      end
      excluded = (section_slugs + GENERIC).map { |s| s.to_s.downcase }

      articles = site.collections['articles']
      return unless articles

      tags = articles.docs
        .flat_map { |a| a.data['categories'] || [] }
        .compact
        .map(&:to_s)
        .uniq
        .reject { |t| excluded.include?(t.downcase) }

      overrides = site.data['tag_overrides'] || {}
      tags.each { |t| site.pages << TagPage.new(site, site.source, t, overrides) }
    end
  end
end
