import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, Calendar } from 'lucide-react';
import { cloudinaryUrl, fetchBlogPost } from '../api';
import usePageMeta from '../hooks/usePageMeta';

export default function BlogPost() {
  const { id } = useParams();

  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  usePageMeta(
    post ? post.title : 'Blog Post',
    post ? (post.meta_description || post.summary || 'Article from Piplad Welfare Foundation.') : 'Read an article from Piplad Welfare Foundation.',
    post && post.image_url
  );

  useEffect(() => {
    let isMounted = true;

    const loadPost = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await fetchBlogPost(id);

        if (isMounted) {
          setPost(data);
        }
      } catch (err) {
        console.error('Failed to fetch blog post:', err);

        if (isMounted) {
          setError(
            err.message || 'Unable to load this blog post.'
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadPost();

    return () => {
      isMounted = false;
    };
  }, [id]);

  const formatDate = (date) => {
    if (!date) return '';

    return new Date(date).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  /*
   * Loading state
   */
  if (loading) {
    return (
      <main
        style={{
          padding: '6rem 1rem',
          textAlign: 'center'
        }}
      >
        Loading article...
      </main>
    );
  }

  /*
   * Error / not found state
   */
  if (error || !post) {
    return (
      <main
        style={{
          padding: '6rem 1rem',
          textAlign: 'center'
        }}
      >
        <h1>Blog Post Not Found</h1>

        <p
          style={{
            color: '#64748b',
            marginBottom: '1.5rem'
          }}
        >
          {error || 'The requested blog post could not be found.'}
        </p>

        <Link
          to="/blog"
          style={{
            color: '#15803d',
            fontWeight: 700
          }}
        >
          ← Back to Blog
        </Link>
      </main>
    );
  }

  return (
    <main className="blog-post-page">

      {/* ================================
          HEADER
      ================================= */}

      <section
        style={{
          background: '#0f172a',
          color: '#ffffff',
          padding: '5rem 0'
        }}
      >
        <div
          className="container"
          style={{
            maxWidth: '1000px'
          }}
        >

          {/* Back to Blog */}
          <Link
            to="/blog"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: '#bbf7d0',
              textDecoration: 'none',
              fontWeight: 600,
              marginBottom: '2rem'
            }}
          >
            <ArrowLeft size={18} />
            Back to Blog
          </Link>

          {/* Blog Title */}
          <h1
            style={{
              fontSize: 'clamp(2.2rem, 5vw, 4rem)',
              lineHeight: 1.15,
              marginBottom: '1.25rem'
            }}
          >
            {post.title}
          </h1>

          {/* Published Date */}
          {post.published_date && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                color: '#cbd5e1'
              }}
            >
              <Calendar size={17} />
              {formatDate(post.published_date)}
            </div>
          )}

        </div>
      </section>


      {/* ================================
          ARTICLE
      ================================= */}

      <section
        style={{
          padding: '4rem 0',
          background: '#ffffff'
        }}
      >
        <article
          className="container"
          style={{
            maxWidth: '900px'
          }}
        >

          {/* ================================
              FEATURED IMAGE
          ================================= */}

          {post.image_url && (
            <div
              style={{
                marginBottom: '3rem',
                borderRadius: '18px',
                overflow: 'hidden'
              }}
            >
              <img
                loading="lazy"
                decoding="async"
                src={cloudinaryUrl(post.image_url, { width: 1200 })}
                alt={post.title}
                style={{
                  width: '100%',
                  maxHeight: '550px',
                  objectFit: 'cover',
                  display: 'block'
                }}
              />
            </div>
          )}


          {/* ================================
              SUMMARY
          ================================= */}

          {post.summary && (
            <p
              style={{
                fontSize: '1.25rem',
                lineHeight: 1.8,
                color: '#475569',
                fontWeight: 500,
                marginBottom: '2rem',
                paddingBottom: '2rem',
                borderBottom: '1px solid #e2e8f0'
              }}
            >
              {post.summary}
            </p>
          )}


          {/* ================================
              WORDPRESS ARTICLE CONTENT
          ================================= */}

          <div
            className="blog-content"
            style={{
              color: '#334155',
              fontSize: '1.05rem',
              lineHeight: 1.9
            }}
            dangerouslySetInnerHTML={{
              __html: post.content || ''
            }}
          />

        </article>
      </section>

    </main>
  );
}